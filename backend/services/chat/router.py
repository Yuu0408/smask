import asyncio

from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.chat.chat_service import ChatService
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, GetChatHistoryRequest

router = APIRouter(prefix="/v1/chat")

@router.post("/new-record", response_model=AddMedicalRecordResponse)
async def create_record(request: AddMedicalRecordRequest, db: Session = Depends(get_session)):
    service = ChatService(db)
    result = await service.create_new_medical_record(request)
    return result

@router.get("")
async def get_chat_history(request: GetChatHistoryRequest, db: Session = Depends(get_session)):
    service = ChatService(db)
    result = await service.get_history(request)
    return result
