import asyncio

from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.chat.chat_service import ChatService
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, ChatTextRequest, ChatTextResponse, GetChatHistoryRequest

router = APIRouter(prefix="/v1/chat")

@router.post("/new-record", response_model=AddMedicalRecordResponse)
async def create_record(request: AddMedicalRecordRequest, db: Session = Depends(get_session)):
    service = ChatService(db)
    result = await service.create_new_medical_record(request)
    return result

@router.get("")
async def get_chat_history(request: GetChatHistoryRequest = Depends(), db: Session = Depends(get_session)):
    service = ChatService(db)
    result = await service.get_history(request)
    return result

@router.post("/chat", response_model=ChatTextResponse)
async def send_message(request: ChatTextRequest, db: Session = Depends(get_session)):
    service = ChatService(db)
    result = await service.process_chat_message(request)
    return result