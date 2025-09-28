import asyncio

from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.record.record_service import RecordService
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, ChatTextRequest, ChatTextResponse, GetCurrentRecordRequest

router = APIRouter(prefix="/v1/record")

# @router.post("/new-record", response_model=AddMedicalRecordResponse)
# async def create_record(request: AddMedicalRecordRequest, db: Session = Depends(get_session)):
#     service = ChatService(db)
#     result = await service.create_new_medical_record(request)
#     return result

@router.get("")
async def get_current_record(request: GetCurrentRecordRequest = Depends(), db: Session = Depends(get_session)):
    service = RecordService(db)
    print(f"Request: {request}")
    result = await service.get_current_record(request)
    return result

# @router.post("/chat", response_model=ChatTextResponse)
# async def send_message(request: ChatTextRequest, db: Session = Depends(get_session)):
#     service = ChatService(db)
#     result = await service.process_chat_message(request)
#     return result