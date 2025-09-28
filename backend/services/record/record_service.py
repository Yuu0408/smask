from services.chat.chat_utils import get_ai_response, get_information
from sqlmodel import Session
from fastapi import HTTPException
from repositories import MedicalRecordRepo, ChatHistoryRepo, AIStateRepo
from models.dto.modelDto import AIStateData, AddMedicalRecordRequest, AddMedicalRecordResponse, ChatMessageDto, ChatTextRequest, ChatTextResponse, GetChatHistoryRequest, GetChatHistoryResponse, GetCurrentRecordRequest, GetCurrentRecordResponse

class RecordService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repo = MedicalRecordRepo(db)
        self.chat_history_repo = ChatHistoryRepo(db)
        self.ai_state_repo = AIStateRepo(db)

    async def get_current_record(self, request: GetCurrentRecordRequest):
        user_id = request.user_id

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')

        record_id = request.record_id if request.record_id else None

        print(f"record_id: {record_id}")
        print(f"user_id: {user_id}")
        
        record = self.medical_record_repo.get_medical_record_by_id(user_id=user_id, record_id=record_id)

        return GetCurrentRecordResponse(
            user_id=str(record.user_id),
            record_id=str(record.record_id),
            data=record.data,
            created_at=record.created_at,
            updated_at=record.updated_at
        )

    async def create_new_medical_record(self, request: AddMedicalRecordRequest):
        user_id = request.user_id
        data = request.data.model_dump(mode="json")

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        
        record = self.medical_record_repo.add_record(user_id=user_id, data=data)
        record_id = record.record_id
        
        ai_response = get_information(record, [], "")
        
        self.ai_state_repo.add_ai_state(
            user_id=user_id, 
            record_id=record_id, 
            data=AIStateData(reasoning="", note="", decision=ai_response.decision).model_dump(mode="json")
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
