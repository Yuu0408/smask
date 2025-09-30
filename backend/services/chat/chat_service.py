from services.chat.chat_utils import get_ai_response, get_conversation_after, get_diagnosis, get_information, update_medical_record
from sqlmodel import Session
from fastapi import HTTPException
from repositories import MedicalRecordRepo, ChatHistoryRepo, AIStateRepo, TodoRepo, DiagnosisRepo
from services.contact.contact_service import ContactService
from services.contact.options import get_allowed_addresses, get_facilities_by_address
from models.dto.modelDto import (
    AIStateData,
    AddMedicalRecordRequest,
    AddMedicalRecordResponse,
    ChatMessageDto,
    ChatTextRequest,
    ChatTextResponse,
    GetChatHistoryRequest,
    GetChatHistoryResponse,
    SendContactRequest,
)

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repo = MedicalRecordRepo(db)
        self.chat_history_repo = ChatHistoryRepo(db)
        self.ai_state_repo = AIStateRepo(db)
        self.todo_repo = TodoRepo(db)
        self.diagnosis_repo = DiagnosisRepo(db)

    async def create_new_medical_record(self, request: AddMedicalRecordRequest):
        user_id = request.user_id
        data = request.data.model_dump(mode="json")

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        
        print(f"Data: {data}")
        
        record = self.medical_record_repo.add_record(user_id=user_id, data=data)
        record_id = record.record_id
        
        # ai_response = get_information(record, [], "")
        
        
        ai_state = self.ai_state_repo.add_ai_state(
            user_id=user_id, 
            record_id=record_id, 
            data=AIStateData(reasoning=None, note="", decision="MAIN_QUESTIONING").model_dump(mode="json")
        )

        # Initialize an empty todo list for this new record
        self.todo_repo.replace_todos(user_id=user_id, record_id=record_id, items=[])

        if ai_state.data["decision"] == "MAIN_QUESTIONING":
            ai_response = get_ai_response(record, ai_state.data["reasoning"] if ai_state else None, ai_state.data["note"] if ai_state else "", [], "", None, "")
            # Normalize nested Pydantic from chain output to our DTO schema
            normalized_reasoning = (
                ai_response.reasoning.model_dump(mode="json")
                if getattr(ai_response, "reasoning", None) is not None and hasattr(ai_response.reasoning, "model_dump")
                else (ai_response.reasoning if getattr(ai_response, "reasoning", None) is not None else None)
            )
            ai_state = self.ai_state_repo.add_ai_state(
                user_id=user_id, 
                record_id=record_id, 
                data=AIStateData(reasoning=normalized_reasoning, note=ai_response.note, decision=ai_response.decision).model_dump(mode="json")
            )
            
        first_bot_message = (getattr(ai_response, "generation", "") or "").strip()
        if first_bot_message:
            messages = [{"role": "ai", "content": first_bot_message}]
            self.chat_history_repo.add_messages(user_id=user_id, record_id=record_id, messages=messages)

        self.db.refresh(record)

        return AddMedicalRecordResponse(
            message=ai_response.generation,
            record_id=str(record_id),
            created_at=record.created_at,
            updated_at=record.updated_at
        )
        
    
    async def get_history(self, request: GetChatHistoryRequest):
        user_id = request.user_id
        record_id = request.record_id

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        
        if not record_id:
            raise HTTPException(status_code=400, detail=f'Invalid record id')
        
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
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        if not record_id:
            raise HTTPException(status_code=400, detail=f'Invalid record id')
        if not message:
            raise HTTPException(status_code=400, detail=f'Message cannot be empty')
        
        chat_history = self.chat_history_repo.get_chat_history(
            user_id=user_id,
            record_id=record_id,
        )

        ai_state = self.ai_state_repo.get_ai_state(user_id=user_id, record_id=record_id)
        medical_record = self.medical_record_repo.get_medical_record_by_id(user_id=user_id, record_id=record_id)

        if ai_state.data["decision"] == "INFORMATION_COLLECTION":
            ai_response = get_information(medical_record, chat_history, message)
            ai_state = self.ai_state_repo.add_ai_state(
                user_id=user_id, 
                record_id=record_id, 
                data=AIStateData(reasoning=None, note="", decision=ai_response.decision).model_dump(mode="json")
            )
        
        diseases_already_asked = set(ai_state.data.get("diseases_already_asked", []))
        disease_to_ask = ai_state.data.get("disease_to_ask", "")

        if ai_state.data["decision"] == "MAIN_QUESTIONING":
            ai_response = get_ai_response(medical_record, ai_state.data["reasoning"] if ai_state else None, ai_state.data["note"] if ai_state else "", chat_history, message, diseases_already_asked, disease_to_ask)
            normalized_reasoning = (
                ai_response.reasoning.model_dump(mode="json")
                if getattr(ai_response, "reasoning", None) is not None and hasattr(ai_response.reasoning, "model_dump")
                else (ai_response.reasoning if getattr(ai_response, "reasoning", None) is not None else None)
            )
            if disease_to_ask != ai_response.disease_to_ask_on_the_next_question:
                diseases_already_asked.add(ai_response.disease_to_ask)
            
            disease_to_ask = ai_response.disease_to_ask_on_the_next_question

            ai_state = self.ai_state_repo.add_ai_state(
                user_id=user_id, 
                record_id=record_id, 
                data=AIStateData(reasoning=normalized_reasoning, note=ai_response.note, decision=ai_response.decision, diseases_already_asked=diseases_already_asked, disease_to_ask=disease_to_ask).model_dump(mode="json")
            )

            messages = [{"role": "human", "content": message}, {"role": "ai", "content": ai_response.generation}]

            self.chat_history_repo.add_messages(user_id=user_id, record_id=record_id, messages=messages)


            return ChatTextResponse(
                message=ai_response.generation,
                multiple_choices=ai_response.multiple_choices if ai_response.multiple_choices else None,
                decision=ai_state.data["decision"] if ai_state.data["decision"] else None
            )
        
        if ai_state.data["decision"] == "DIAGNOSIS":
            message = "###DIAGNOSIS###"
            ai_response = get_diagnosis(medical_record, chat_history, ai_state.data["note"] if ai_state else "")
            current_state = ai_state.data if ai_state and hasattr(ai_state, "data") else {}
            # Also persist todos independently using TodoRepo
            normalized_todos = []
            if getattr(ai_response, "todo", None):
                try:
                    for t in ai_response.todo:
                        normalized_todos.append((str(t), False))
                except Exception:
                    normalized_todos = []
            if normalized_todos:
                self.todo_repo.replace_todos(user_id=user_id, record_id=record_id, items=normalized_todos)

            # Persist diagnosis into its own table
            self.diagnosis_repo.add_diagnosis(
                user_id=user_id,
                record_id=record_id,
                reasoning_process=ai_response.reasoning_process,
                diagnosis=(ai_response.diagnosis.model_dump(mode="json") if hasattr(ai_response.diagnosis, "model_dump") else ai_response.diagnosis),
                further_test=[
                    (item.model_dump(mode="json") if hasattr(item, "model_dump") else item)
                    for item in (ai_response.further_test or [])
                ],
            )

            new_state = {
                **(current_state or {}),
                "reasoning": None,
                "note": "",
                "decision": "FINAL_STEPS",
            }
            ai_state = self.ai_state_repo.add_ai_state(
                user_id=user_id,
                record_id=record_id,
                data=new_state,
            )

            updated_medical_record_data = ai_response.medical_record
            if hasattr(updated_medical_record_data, "model_dump"):
                medical_record.data = updated_medical_record_data.model_dump(mode="json")
            else:
                medical_record.data = updated_medical_record_data
            self.medical_record_repo.update_record(medical_record)
        
        if ai_state.data["decision"] == "FINAL_STEPS":
            print("Getting final steps...")
            latest = self.diagnosis_repo.get_latest(user_id=user_id, record_id=record_id)
            diagnosis_for_followup = {
                "reasoning_process": getattr(latest, "reasoning_process", ""),
                "diagnosis": getattr(latest, "diagnosis", {}),
                "further_test": getattr(latest, "further_test", {}),
            } if latest else {}
            ai_response = get_conversation_after(diagnosis=diagnosis_for_followup, history=chat_history, medical_record=medical_record, message=message)
            # Agent action: auto-send contact if collected
            try:
                if str(getattr(ai_response, 'action', '')).upper() == 'SEND_CONTACT':
                    details = getattr(ai_response, 'send_contact', None) or {}
                    include_conversation = bool(details.get('include_conversation'))
                    address = (details.get('address') or '').strip()
                    facility = (details.get('facility') or '').strip()
                    allowed_addresses = get_allowed_addresses()
                    facilities_map = get_facilities_by_address()
                    if address in allowed_addresses and facility in (facilities_map.get(address) or []):
                        svc = ContactService(self.db)
                        await svc.send(SendContactRequest(
                            user_id=str(user_id),
                            record_id=str(record_id),
                            include_conversation=include_conversation,
                            address=address,
                            facility=facility,
                        ))
            except Exception:
                # Do not break the conversation on send failure
                pass
            merged_state = {
                **(ai_state.data if ai_state and hasattr(ai_state, "data") else {}),
                "reasoning": None,
                "note": "",
                "decision": "FINAL_STEPS",
            }
            ai_state = self.ai_state_repo.add_ai_state(
                user_id=user_id,
                record_id=record_id,
                data=merged_state,
            )

        if message == "###DIAGNOSIS###":
            messages = [{"role": "ai", "content": ai_response.generation}]
        else:
            messages = [{"role": "human", "content": message}, {"role": "ai", "content": ai_response.generation}]

        self.chat_history_repo.add_messages(user_id=user_id, record_id=record_id, messages=messages)

        return ChatTextResponse(
            message=ai_response.generation,
            multiple_choices=ai_response.multiple_choices if ai_response.multiple_choices else None,
            decision=ai_state.data["decision"] if ai_state.data["decision"] else None
        )





