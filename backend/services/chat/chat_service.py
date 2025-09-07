from services.chat.chat_utils import get_ai_response
from sqlmodel import Session
from fastapi import HTTPException
from repositories import MedicalRecordRepo, ChatHistoryRepo, AIStateRepo
from models.dto.modelDto import AIStateData, AddMedicalRecordRequest, AddMedicalRecordResponse, ChatMessageDto, ChatTextRequest, ChatTextResponse, GetChatHistoryRequest, GetChatHistoryResponse

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repo = MedicalRecordRepo(db)
        self.chat_history_repo = ChatHistoryRepo(db)
        self.ai_state_repo = AIStateRepo(db)

    async def create_new_medical_record(self, request: AddMedicalRecordRequest):
        user_id = request.user_id
        data = request.data.model_dump(mode="json")

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        
        record = self.medical_record_repo.add_record(user_id=user_id, data=data)

        record_id = record.record_id
        self.ai_state_repo.add_ai_state(
            user_id=user_id, 
            record_id=record_id, 
            data=AIStateData(reasoning="", note="", decision="CONVERSATION").model_dump(mode="json")
        )
        
        ai_response = get_ai_response(record, "", [], "")
        
        self.ai_state_repo.add_ai_state(
            user_id=user_id, 
            record_id=record_id, 
            data=AIStateData(reasoning=ai_response.reasoning, note=ai_response.note, decision="CONVERSATION").model_dump(mode="json")
        )
        messages = [{"role": "ai", "content": ai_response.generation}]
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

        ai_response = get_ai_response(medical_record, ai_state.data["reasoning"] if ai_state else "", chat_history, message)

        messages = [{"role": "human", "content": message}, {"role": "ai", "content": ai_response.generation}]

        self.chat_history_repo.add_messages(user_id=user_id, record_id=record_id, messages=messages)

        self.ai_state_repo.add_ai_state(
            user_id=user_id, 
            record_id=record_id, 
            data=AIStateData(reasoning=ai_response.reasoning, note=ai_response.note, decision=ai_response.decision).model_dump(mode="json")
        )

        return ChatTextResponse(
            message=ai_response.generation,
            multiple_choices=ai_response.multiple_choices if ai_response.multiple_choices else None
        )