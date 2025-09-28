import asyncio
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.history.history_service import HistoryService
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, ChatTextRequest, ChatTextResponse, GetAllChatHistoryRequest, GetChatHistoryRequest

router = APIRouter(prefix="/v1/history")

# @router.post("/rd", response_model=AddMedicalRecordResponse)
# async def create_record(request: AddMedicalRecordRequest, db: Session = Depends(get_session)):
#     service = ChatService(db)
#     result = await service.create_new_medical_record(request)
#     return result

@router.get("")
async def get_all_chat_history(request: GetAllChatHistoryRequest = Depends(), db: Session = Depends(get_session)):
    service = HistoryService(db)
    result = await service.get_all_history(request)
    return result