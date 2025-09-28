from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.contact.contact_service import ContactService
from models.dto.modelDto import (
    SendContactRequest, SendContactResponse,
    ListPatientsRequest, ListPatientsResponse,
    GetContactDetailRequest, ContactDetailResponse,
    ContactMessageRequest, ContactMessageDto, ContactMessagesResponse, MyDoctorsResponse
)

router = APIRouter(prefix="/v1/contact")

@router.post("/send", response_model=SendContactResponse)
async def send_contact(request: SendContactRequest, db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.send(request)

@router.get("/patients", response_model=ListPatientsResponse)
async def list_patients(request: ListPatientsRequest = Depends(), db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.list_patients(request)

@router.get("/detail", response_model=ContactDetailResponse)
async def contact_detail(request: GetContactDetailRequest = Depends(), db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.detail(request)

@router.get("/messages", response_model=ContactMessagesResponse)
async def get_messages(contact_id: str, db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.get_messages(contact_id)

@router.post("/message", response_model=ContactMessageDto)
async def send_message(request: ContactMessageRequest, db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.send_message(request)

@router.get("/my-doctors", response_model=MyDoctorsResponse)
async def my_doctors(patient_id: str, db: Session = Depends(get_session)):
    svc = ContactService(db)
    return await svc.my_doctors(patient_id)


