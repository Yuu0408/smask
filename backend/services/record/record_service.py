from sqlmodel import Session
from fastapi import HTTPException
from repositories import MedicalRecordRepo, ChatHistoryRepo, AIStateRepo
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, ChatMessageDto, ChatTextRequest, ChatTextResponse, GetChatHistoryRequest, GetChatHistoryResponse, GetCurrentRecordRequest, GetCurrentRecordResponse
from services.chat.chat_service import ChatService

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
        # Delegate to the chat service to ensure consistent initialization and state handling
        chat_service = ChatService(self.db)
        return await chat_service.create_new_medical_record(request)
