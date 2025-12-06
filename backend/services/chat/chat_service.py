import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID as UUID_cls

from fastapi import HTTPException
from sqlmodel import Session

from models.dto.modelDto import (
    AIStateData,
    AddMedicalRecordRequest,
    AddMedicalRecordResponse,
    ChatMessageDto,
    ChatTextRequest,
    ChatTextResponse,
    GetChatHistoryRequest,
    GetChatHistoryResponse,
    PendingQuestion,
    ReasoningCandidate,
    ReasoningSnapshot,
    SharedState,
    TodoItem,
)
from repositories import AIStateRepo, ChatHistoryRepo, DiagnosisRepo, MedicalRecordRepo, TodoRepo
from repositories.contact_repo import ContactRepo
from services.chat.chat_utils import (
    run_basic_question,
    run_closing,
    run_diagnostic_reasoning,
    run_form_clarification,
    run_final_diagnosis,
    run_record_update,
    run_next_step,
    run_rule_out_selection,
    run_rule_out_question,
    run_state_update,
)
from services.chat.state_manager import (
    STAGE_BASIC,
    STAGE_CLOSING,
    STAGE_NEXT_STEP,
    STAGE_FORM,
    STAGE_REASON,
    STAGE_RULE_OUT,
    apply_state_update,
    build_initial_state,
    next_stage_after_rule_out,
    set_last_question,
    should_enter_reasoning,
    update_conversation_tail,
)


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repo = MedicalRecordRepo(db)
        self.chat_history_repo = ChatHistoryRepo(db)
        self.ai_state_repo = AIStateRepo(db)
        self.todo_repo = TodoRepo(db)
        self.diagnosis_repo = DiagnosisRepo(db)
        self.contact_repo = ContactRepo(db)

    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge overlay into base without mutating inputs."""
        if base is None:
            base = {}
        merged = {**(base or {})}
        for key, value in (overlay or {}).items():
            if (
                isinstance(value, dict)
                and isinstance(merged.get(key), dict)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    # ------------ Helpers ------------
    def _load_state(self, ai_state_record, form_payload: Dict[str, Any]) -> AIStateData:
        try:
            return AIStateData.model_validate(ai_state_record.data)
        except Exception:
            return build_initial_state(form_payload)

    def _reasoning_snapshot_from_output(self, output) -> ReasoningSnapshot:
        def to_candidate(item) -> ReasoningCandidate:
            raw = item.model_dump() if hasattr(item, "model_dump") else dict(item)
            return ReasoningCandidate(
                name=raw.get("name", ""),
                likelihood=raw.get("likelihood", "medium"),
                supporting=raw.get("supporting", []) or [],
                missing=raw.get("missing", []) or [],
                conflicts=raw.get("conflicts", []) or [],
                priority=raw.get("priority", "standard"),
            )

        raw = output.model_dump() if hasattr(output, "model_dump") else dict(output)
        return ReasoningSnapshot(
            summary=raw.get("summary", ""),
            high_priority=[to_candidate(x) for x in raw.get("high_priority", [])],
            differentials=[to_candidate(x) for x in raw.get("differentials", [])],
            rule_out=[to_candidate(x) for x in raw.get("rule_out", [])],
            recommended_tests=raw.get("recommended_tests", []) or [],
            needs_more_questions=bool(raw.get("needs_more_questions", True)),
            good_conclusion=bool(raw.get("good_conclusion", False)),
            refresh_reason=raw.get("refresh_reason") or None,
        )

    def _save_state(self, user_id, record_id, state: AIStateData):
        return self.ai_state_repo.add_ai_state(
            user_id=user_id, record_id=record_id, data=state.model_dump(mode="json")
        )

    # ------------ API entrypoints ------------
    async def create_new_medical_record(self, request: AddMedicalRecordRequest):
        user_id = request.user_id
        data = request.data.model_dump(mode="json")

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user id")

        record = self.medical_record_repo.add_record(user_id=user_id, data=data)
        record_id = record.record_id

        ai_state = build_initial_state(form_payload=data)
        shared = ai_state.shared_state

        # Block 1: form validation / clarification
        form_out = run_form_clarification(shared_state=shared, latest_message="")
        shared = apply_state_update(
            shared,
            {
                "clarified_form": getattr(form_out, "clarified_form", {}) or {},
                "red_flags": getattr(form_out, "red_flags", []) or [],
                "info_gaps_basic": getattr(form_out, "missing_fields", []) or [],
            },
        )

        response_text = ""
        options: List[str] = []

        if getattr(form_out, "ready_for_basic", False) and not getattr(form_out, "question", ""):
            ai_state.stage = STAGE_BASIC
        else:
            ai_state.stage = STAGE_BASIC if getattr(form_out, "ready_for_basic", False) else STAGE_FORM
            response_text = getattr(form_out, "question", "") or ""
            options = getattr(form_out, "options", []) or []
            if response_text:
                shared = set_last_question(
                    shared,
                    response_text,
                    intent="clarify_form",
                    target=None,
                    options=options,
                    rationale=getattr(form_out, "rationale", None),
                )

        # If no clarification needed, start with the first basic question
        if ai_state.stage == STAGE_BASIC and not response_text:
            basic_out = run_basic_question(shared_state=shared)
            shared.red_flags = sorted(
                set(shared.red_flags + (getattr(basic_out, "red_flags", []) or []))
            )
            response_text = getattr(basic_out, "question", "")
            options = getattr(basic_out, "options", []) or []
            shared = set_last_question(
                shared,
                response_text,
                intent="basic_symptom",
                target=getattr(basic_out, "target_symptom", None),
                options=options,
                rationale=getattr(basic_out, "rationale", None),
            )
            ai_state.stage = (
                STAGE_REASON if getattr(basic_out, "ready_for_reasoning", False) else STAGE_BASIC
            )

        if response_text:
            shared = update_conversation_tail(shared, [{"role": "ai", "content": response_text}])
        ai_state.shared_state = shared
        self._save_state(user_id=user_id, record_id=record_id, state=ai_state)

        # Initialize an empty todo list (kept for compatibility)
        self.todo_repo.replace_todos(user_id=user_id, record_id=record_id, items=[])

        self.db.refresh(record)

        if response_text:
            self.chat_history_repo.add_messages(
                user_id=user_id,
                record_id=record_id,
                messages=[{"role": "ai", "content": response_text}],
            )
        else:
            raise HTTPException(status_code=500, detail="Unable to generate initial question")

        return AddMedicalRecordResponse(
            message=response_text,
            record_id=str(record_id),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def get_history(self, request: GetChatHistoryRequest):
        user_id = request.user_id
        record_id = request.record_id

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user id")

        if not record_id:
            raise HTTPException(status_code=400, detail="Invalid record id")

        rows = self.chat_history_repo.get_chat_history(
            user_id=request.user_id,
            record_id=request.record_id,
        )
        return GetChatHistoryResponse(
            history=[
                ChatMessageDto(
                    id=str(row.id),
                    role=row.role,
                    content=row.content,
                    created_at=row.created_at,
                )
                for row in rows
            ]
        )

    async def process_chat_message(self, request: ChatTextRequest):
        user_id = request.user_id
        record_id = request.record_id
        message = request.message

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user id")
        if not record_id:
            raise HTTPException(status_code=400, detail="Invalid record id")
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        ai_state_record = self.ai_state_repo.get_ai_state(user_id=user_id, record_id=record_id)
        medical_record = self.medical_record_repo.get_medical_record_by_id(
            user_id=user_id, record_id=record_id
        )
        form_payload = getattr(medical_record, "data", {}) or {}

        state_data = self._load_state(ai_state_record, form_payload)
        shared: SharedState = state_data.shared_state

        # Keep the conversation history for tone/context
        shared = update_conversation_tail(shared, [{"role": "human", "content": message}])

        response_stage_override = None

        # Skip state-update LLM when we're already at final/next-step stage
        major_change = False
        if state_data.stage not in {STAGE_CLOSING, STAGE_NEXT_STEP}:
            last_question_payload: Dict[str, Any] = (
                shared.last_question.model_dump(mode="json")
                if isinstance(shared.last_question, PendingQuestion)
                else shared.last_question
            )

            # Update shared state with the patient's latest answer/statement
            state_update = run_state_update(
                shared_state=shared, last_question=last_question_payload, patient_message=message
            )
            update_dict = (
                state_update.model_dump(mode="json")
                if hasattr(state_update, "model_dump")
                else dict(state_update)
            )
            major_change = bool(update_dict.get("major_change"))
            shared = apply_state_update(shared, update_dict)

        response_text = ""
        options: List[str] = []
        action: Optional[str] = None
        send_contact: Optional[dict] = None
        todos_payload: Optional[List[TodoItem]] = None
        closing_out = None
        stage = state_data.stage

        # Conditional block after rule-out answers
        if stage == STAGE_RULE_OUT:
            stage = next_stage_after_rule_out(shared, major_change=major_change)

        # Block 1: Form clarification
        if stage == STAGE_FORM and not response_text:
            form_out = run_form_clarification(shared_state=shared, latest_message=message)
            shared = apply_state_update(
                shared,
                {
                    "clarified_form": getattr(form_out, "clarified_form", {}) or {},
                    "red_flags": getattr(form_out, "red_flags", []) or [],
                    "info_gaps_basic": getattr(form_out, "missing_fields", []) or [],
                },
            )
            if getattr(form_out, "ready_for_basic", False) and not getattr(form_out, "question", ""):
                stage = STAGE_BASIC
            else:
                stage = STAGE_BASIC if getattr(form_out, "ready_for_basic", False) else STAGE_FORM
                response_text = getattr(form_out, "question", "") or ""
                options = getattr(form_out, "options", []) or []
                if response_text:
                    shared = set_last_question(
                        shared,
                        response_text,
                        intent="clarify_form",
                        target=None,
                        options=options,
                        rationale=getattr(form_out, "rationale", None),
                    )

        # Block 2: Principle-based basic questions
        if stage == STAGE_BASIC and not response_text:
            go_reasoning, _ = should_enter_reasoning(shared)
            if go_reasoning:
                stage = STAGE_REASON
            else:
                basic_out = run_basic_question(shared_state=shared)
                shared.red_flags = sorted(
                    set(shared.red_flags + (getattr(basic_out, "red_flags", []) or []))
                )
                response_text = getattr(basic_out, "question", "")
                options = getattr(basic_out, "options", []) or []
                shared = set_last_question(
                    shared,
                    response_text,
                    intent="basic_symptom",
                    target=getattr(basic_out, "target_symptom", None),
                    options=options,
                    rationale=getattr(basic_out, "rationale", None),
                )
                stage = (
                    STAGE_REASON
                    if getattr(basic_out, "ready_for_reasoning", False)
                    else STAGE_BASIC
                )

        # Block 3: Initial diagnostic reasoning (no direct question)
        if stage == STAGE_REASON and not response_text:
            reasoning_out = run_diagnostic_reasoning(shared_state=shared)
            shared.reasoning_snapshot = self._reasoning_snapshot_from_output(reasoning_out)
            stage = STAGE_CLOSING if shared.reasoning_snapshot.good_conclusion else STAGE_RULE_OUT

        # Block 4: Rule-out / rule-in questioning
        if stage == STAGE_RULE_OUT and not response_text:
            selection = run_rule_out_selection(shared_state=shared)
            selection_payload = (
                selection.model_dump(mode="json") if hasattr(selection, "model_dump") else dict(selection)
            )
            # Attach selection plan into shared state for transparency
            shared.selection_plan = selection_payload  # type: ignore[attr-defined]

            # If patient requested to conclude and selection allows, hand off to closing
            if selection_payload.get("handoff_to_closing"):
                stage = STAGE_CLOSING
            else:
                rule_out_out = run_rule_out_question(shared_state=shared, selection_plan=selection_payload)
                response_text = getattr(rule_out_out, "question", "")
                options = getattr(rule_out_out, "options", []) or []
                shared = set_last_question(
                    shared,
                    response_text,
                    intent="rule_out",
                    target=getattr(rule_out_out, "target_condition", None)
                    or selection_payload.get("target_condition"),
                    options=options,
                    rationale=getattr(rule_out_out, "rationale", None),
                )
                snapshot = shared.reasoning_snapshot
                if snapshot and getattr(rule_out_out, "allow_finish_if_clear", False):
                    snapshot.needs_more_questions = False
                    snapshot.refresh_reason = None
                    snapshot.good_conclusion = snapshot.good_conclusion or False

        # Closing message
        if stage == STAGE_CLOSING and not response_text:
            record_update_out = None
            final_diag_out = None

            # Run record update + final diagnosis in parallel to avoid serial OpenAI calls
            record_update_task = asyncio.create_task(
                asyncio.to_thread(run_record_update, shared_state=shared)
            )
            final_diag_task = asyncio.create_task(
                asyncio.to_thread(run_final_diagnosis, shared_state=shared)
            )
            record_update_result, final_diag_result = await asyncio.gather(
                record_update_task, final_diag_task, return_exceptions=True
            )

            # Apply record updates if available
            if not isinstance(record_update_result, Exception):
                record_update_out = record_update_result
                try:
                    record_update_payload = (
                        record_update_out.model_dump(mode="json")
                        if hasattr(record_update_out, "model_dump")
                        else dict(record_update_out)
                    )
                    updates = record_update_payload.get("record_updates") or {}
                    if updates:
                        shared.clarified_form = self._deep_merge(shared.clarified_form or {}, updates)
                        merged_form = self._deep_merge(getattr(medical_record, "data", {}) or {}, updates)
                        medical_record.data = merged_form
                        self.medical_record_repo.update_record(medical_record)
                except Exception:
                    record_update_out = None
            # Capture diagnosis result even if record update fails
            if not isinstance(final_diag_result, Exception):
                final_diag_out = final_diag_result

            closing_out = run_closing(shared_state=shared)
            response_text = getattr(closing_out, "message", "")
            options = getattr(closing_out, "options", []) or []
            action = getattr(closing_out, "action", None)
            send_contact = getattr(closing_out, "send_contact", None)
            response_stage_override = STAGE_CLOSING
            shared.last_question = None
            shared.pending_questions = []

            # Persist clarified form back to the medical record
            try:
                merged_form = self._deep_merge(getattr(medical_record, "data", {}) or {}, shared.clarified_form or {})
                medical_record.data = merged_form
                self.medical_record_repo.update_record(medical_record)
            except Exception:
                # Non-fatal: keep going even if persistence fails
                pass

            # Persist diagnosis (prefer final diagnosis output, fall back to snapshot)
            try:
                if final_diag_out:
                    diag_payload = (
                        final_diag_out.model_dump(mode="json")
                        if hasattr(final_diag_out, "model_dump")
                        else dict(final_diag_out)
                    )
                    diag_reasoning = diag_payload.get("reasoning_process") or ""
                    diag_body = diag_payload.get("diagnosis") or {}
                    diag_tests = diag_payload.get("further_test") or []
                    self.diagnosis_repo.add_diagnosis(
                        user_id=UUID_cls(user_id),
                        record_id=UUID_cls(record_id),
                        reasoning_process=diag_reasoning,
                        diagnosis=diag_body,
                        further_test=diag_tests,
                    )
                elif shared.reasoning_snapshot:
                    snapshot_dict = shared.reasoning_snapshot.model_dump(mode="json")
                    further_tests = snapshot_dict.get("recommended_tests") or []
                    self.diagnosis_repo.add_diagnosis(
                        user_id=UUID_cls(user_id),
                        record_id=UUID_cls(record_id),
                        reasoning_process=snapshot_dict.get("summary") or "",
                        diagnosis=snapshot_dict,
                        further_test=further_tests,
                    )
            except Exception:
                # Non-fatal: continue flow even if diagnosis persistence fails
                pass

            # Build and persist todo list (recommended tests / recommendations)
            todo_items: List[tuple[str, bool]] = []
            snapshot = shared.reasoning_snapshot
            if snapshot and snapshot.recommended_tests:
                todo_items.extend([(text, False) for text in snapshot.recommended_tests if text])
            recommendation_text = getattr(closing_out, "recommendation", "") if closing_out else ""
            if recommendation_text:
                todo_items.append((recommendation_text, False))
            try:
                rows = self.todo_repo.replace_todos(
                    user_id=user_id, record_id=record_id, items=todo_items
                )
                todos_payload = [TodoItem(text=row.text, is_check=row.is_check) for row in rows if row.text]
            except Exception:
                todos_payload = None

            # If asked to send contact, create the contact record immediately
            contact_id = None
            if action == "SEND_CONTACT" and send_contact:
                # Prepare extra payload (reasoning snapshot) to attach to contact
                reasoning_snapshot_payload = None
                if shared.reasoning_snapshot:
                    reasoning_snapshot_payload = shared.reasoning_snapshot.model_dump(mode="json")
                try:
                    contact_row = self.contact_repo.create_contact(
                        patient_id=UUID_cls(user_id),
                        record_id=UUID_cls(record_id),
                        address=send_contact.get("address"),
                        facility=send_contact.get("facility"),
                        include_conversation=bool(send_contact.get("include_conversation")),
                        payload_extra={
                            "reasoning_snapshot": reasoning_snapshot_payload,
                        },
                    )
                    contact_id = str(contact_row.id)
                except HTTPException as e:
                    if e.status_code == 409:
                        # Already sent; ignore to avoid blocking
                        action = "NONE"
                    else:
                        raise
                except Exception:
                    action = "NONE"

                if send_contact and contact_id:
                    send_contact = {**send_contact, "contact_id": contact_id}

            # After the final block, transition to the next-step stage
            stage = STAGE_NEXT_STEP

        # Next-step follow-ups: rely on conversation history only
        if stage == STAGE_NEXT_STEP and not response_text:
            next_step_out = run_next_step(shared_state=shared)
            response_text = getattr(next_step_out, "message", "")
            options = getattr(next_step_out, "options", []) or []
            action = getattr(next_step_out, "action", None)
            send_contact = getattr(next_step_out, "send_contact", None)
            response_stage_override = STAGE_NEXT_STEP
            shared.last_question = None
            shared.pending_questions = []

            contact_id = None
            if action == "SEND_CONTACT" and send_contact:
                reasoning_snapshot_payload = None
                if shared.reasoning_snapshot:
                    reasoning_snapshot_payload = shared.reasoning_snapshot.model_dump(mode="json")
                try:
                    contact_row = self.contact_repo.create_contact(
                        patient_id=UUID_cls(user_id),
                        record_id=UUID_cls(record_id),
                        address=send_contact.get("address"),
                        facility=send_contact.get("facility"),
                        include_conversation=bool(send_contact.get("include_conversation")),
                        payload_extra={
                            "reasoning_snapshot": reasoning_snapshot_payload,
                        },
                    )
                    contact_id = str(contact_row.id)
                except HTTPException as e:
                    if e.status_code == 409:
                        # Already sent; ignore to avoid blocking
                        action = "NONE"
                    else:
                        raise
                except Exception:
                    action = "NONE"

                if send_contact and contact_id:
                    send_contact = {**send_contact, "contact_id": contact_id}

        if not response_text:
            raise HTTPException(status_code=500, detail="Unable to generate response for current stage")

        shared = update_conversation_tail(shared, [{"role": "ai", "content": response_text}])
        state_data.stage = stage
        state_data.shared_state = shared
        self._save_state(user_id=user_id, record_id=record_id, state=state_data)

        # Persist chat history
        self.chat_history_repo.add_messages(
            user_id=user_id,
            record_id=record_id,
            messages=[
                {"role": "human", "content": message},
                {"role": "ai", "content": response_text},
            ],
        )

        return ChatTextResponse(
            message=response_text,
            multiple_choices=options or None,
            decision=response_stage_override or state_data.stage,
            action=action,
            send_contact=send_contact,
            todos=todos_payload,
        )
