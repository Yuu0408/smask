import asyncio

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from database import get_session
from services.chat.chat_service import ChatService
from models.dto.modelDto import AddMedicalRecordRequest, AddMedicalRecordResponse, ChatTextRequest, ChatTextResponse, GetChatHistoryRequest, TTSRequest
from services.voice.tts import synthesize_speech
import base64

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


@router.post("/voice")
async def send_voice_message(request: ChatTextRequest, db: Session = Depends(get_session)):
    """Process a chat message and return both text and TTS audio (base64)."""
    service = ChatService(db)
    result = await service.process_chat_message(request)
    audio_bytes = synthesize_speech(result.message)
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    return {"text": result.message, "audio_b64": audio_b64, "content_type": "audio/mpeg"}


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Synthesize arbitrary text to speech (for initial AI message)."""
    audio_bytes = synthesize_speech(request.text, request.voice_id)
    return Response(content=audio_bytes, media_type="audio/mpeg")
