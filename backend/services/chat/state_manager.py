from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple
from uuid import uuid4

from models.dto.modelDto import (
    AIStateData,
    PendingQuestion,
    ReasoningSnapshot,
    SharedState,
    SymptomNote,
)

# Stages used by the new flow
STAGE_FORM = "FORM_CLARIFICATION"
STAGE_BASIC = "BASIC_QUESTIONING"
STAGE_REASON = "REASONING"
STAGE_RULE_OUT = "RULE_OUT"
STAGE_CLOSING = "CLOSING"


def _safe_get(mapping: Dict[str, Any], *path: str) -> Any:
    cursor: Any = mapping
    for key in path:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def _detect_basic_gaps(form_payload: Dict[str, Any]) -> List[str]:
    """Return human-readable missing fields from the intake form."""
    required_fields = [
        ("patient_info", "full_name"),
        ("patient_info", "birthday"),
        ("patient_info", "gender"),
        ("patient_info", "occupation"),
        ("patient_info", "nationality"),
        ("medical_history", "chief_complaint"),
        ("medical_history", "medical_history"),
    ]
    missing = []
    for path in required_fields:
        value = _safe_get(form_payload, *path)
        if value in (None, "", []):
            missing.append(".".join(path))
    return missing


def _trim_tail(existing: List[dict], new_entries: Iterable[dict], limit: Optional[int] = None) -> List[dict]:
    """Append new entries to the full conversation log; optionally trim if a limit is provided."""
    tail = (existing or []) + list(new_entries)
    if limit is None:
        return tail
    return tail[-limit:]


def build_initial_state(form_payload: Dict[str, Any]) -> AIStateData:
    """Create an initial shared state from the submitted form."""
    basic_form = form_payload or {}
    state = SharedState(
        basic_form=basic_form,
        clarified_form={},
        symptom_notes=[],
        red_flags=[],
        info_gaps_basic=_detect_basic_gaps(basic_form),
        info_gaps_symptom=[],
        reasoning_snapshot=None,
        pending_questions=[],
        last_question=None,
        conversation_tail=[],
    )
    return AIStateData(shared_state=state, stage=STAGE_FORM)


def merge_symptom_notes(current: List[SymptomNote], updates: List[SymptomNote]) -> List[SymptomNote]:
    """Merge symptom notes by summary text (case-insensitive)."""
    merged = {note.summary.lower(): note for note in current}
    for upd in updates:
        key = upd.summary.lower()
        if key in merged:
            existing = merged[key]
            merged[key] = SymptomNote(
                summary=existing.summary,
                detail=upd.detail or existing.detail,
                status=upd.status or existing.status,
                source=upd.source or existing.source,
                linked=sorted(set(existing.linked + upd.linked)),
                onset=upd.onset or existing.onset,
                severity=upd.severity or existing.severity,
            )
        else:
            merged[key] = upd
    return list(merged.values())


def apply_state_update(shared: SharedState, update: Dict[str, Any]) -> SharedState:
    """Apply LLM-proposed state deltas into the shared state."""
    if not update:
        return shared

    last_question_id = getattr(shared.last_question, "id", None)

    clarified_form = update.get("clarified_form") or {}
    red_flags = update.get("red_flags") or []
    info_gaps_basic = update.get("info_gaps_basic")
    info_gaps_symptom = update.get("info_gaps_symptom")
    symptoms_payload = update.get("symptom_notes") or []

    # Rehydrate symptom notes into objects if they came as dicts
    new_symptoms: List[SymptomNote] = []
    for item in symptoms_payload:
        if isinstance(item, SymptomNote):
            new_symptoms.append(item)
        elif isinstance(item, dict):
            try:
                new_symptoms.append(SymptomNote(**item))
            except Exception:
                continue
        elif isinstance(item, str):
            # Allow LLM to return bare symptom strings; coerce to SymptomNote
            new_symptoms.append(
                SymptomNote(
                    summary=item,
                    detail=None,
                    status="reported",
                    source="patient",
                    linked=[],
                    onset=None,
                    severity=None,
                )
            )

    merged_symptoms = merge_symptom_notes(shared.symptom_notes, new_symptoms)

    remaining_pending = []
    for pending in shared.pending_questions:
        if last_question_id and getattr(pending, "id", None) == last_question_id:
            continue
        remaining_pending.append(pending)

    updated = SharedState(
        basic_form=shared.basic_form,
        clarified_form={**shared.clarified_form, **clarified_form},
        symptom_notes=merged_symptoms,
        red_flags=sorted(set(shared.red_flags + red_flags)),
        info_gaps_basic=info_gaps_basic if info_gaps_basic is not None else shared.info_gaps_basic,
        info_gaps_symptom=info_gaps_symptom if info_gaps_symptom is not None else shared.info_gaps_symptom,
        reasoning_snapshot=shared.reasoning_snapshot,
        pending_questions=remaining_pending,
        last_question=None,  # consumed after update
        asked_targets=shared.asked_targets,
        conversation_tail=shared.conversation_tail,
    )
    return updated


def set_last_question(shared: SharedState, question_text: str, *, intent: str, target: Optional[str], options: List[str], rationale: Optional[str] = None) -> SharedState:
    if not question_text:
        return shared
    pending = PendingQuestion(
        id=str(uuid4()),
        text=question_text,
        options=options or [],
        target=target,
        intent=intent,  # type: ignore[arg-type]
        rationale=rationale,
    )
    shared.last_question = pending
    shared.pending_questions.append(pending)
    if target:
        shared.asked_targets = sorted(set(shared.asked_targets + [target]))
    else:
        shared.asked_targets = sorted(set(shared.asked_targets + [question_text.strip().lower()]))
    return shared


def update_conversation_tail(shared: SharedState, new_entries: Iterable[dict]) -> SharedState:
    shared.conversation_tail = _trim_tail(shared.conversation_tail, new_entries)
    return shared


def should_enter_reasoning(shared: SharedState) -> Tuple[bool, str]:
    """Conditional block between basic questioning and reasoning.

    - If any red flags present -> escalate to reasoning.
    - If no red flags and symptom gaps remain -> continue basic questions.
    - Otherwise move to reasoning once at least two symptoms are logged.
    """
    if shared.red_flags:
        return True, "red_flag"
    if shared.info_gaps_symptom:
        return False, "need_more_basic_symptom_info"
    if len(shared.symptom_notes) >= 2:
        return True, "sufficient_symptom_coverage"
    return False, "insufficient_symptom_depth"


def next_stage_after_rule_out(shared: SharedState, *, major_change: bool = False) -> str:
    """Decide whether to loop questions, re-run reasoning, or finish."""
    snapshot: Optional[ReasoningSnapshot] = shared.reasoning_snapshot
    if major_change or snapshot is None or snapshot.refresh_reason:
        return STAGE_REASON
    if snapshot.good_conclusion:
        return STAGE_CLOSING
    if snapshot.needs_more_questions:
        return STAGE_RULE_OUT
    # Default: re-run reasoning to tighten ranks
    return STAGE_REASON
