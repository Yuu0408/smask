from uuid import UUID
from sqlmodel import Session
from fastapi import HTTPException

from repositories.contact_repo import ContactRepo
from models.entities.model import User
from models.dto.modelDto import (
    SendContactRequest, SendContactResponse,
    ListPatientsRequest, ListPatientsResponse, PatientCard,
    GetContactDetailRequest, ContactDetailResponse,
    ContactMessageRequest, ContactMessagesResponse, ContactMessageDto,
    MyDoctorsResponse, ChatMessageDto, TodoItem
)


class ContactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContactRepo(db)

    async def send(self, req: SendContactRequest) -> SendContactResponse:
        c = self.repo.create_contact(
            patient_id=UUID(req.user_id),
            record_id=UUID(req.record_id),
            address=req.address,
            facility=req.facility,
            include_conversation=req.include_conversation,
        )
        return SendContactResponse(ok=True, contact_id=str(c.id))

    async def list_patients(self, req: ListPatientsRequest) -> ListPatientsResponse:
        rows = self.repo.list_for_doctor(doctor_id=UUID(req.doctor_id))
        cards: list[PatientCard] = []
        for c in rows:
            mr = (c.payload or {}).get("medical_record", {}) or {}
            pi = mr.get("patient_info", {}) or {}
            full_name = pi.get("full_name", "Unknown")
            # derive age
            age = 0
            try:
                bday = pi.get("birthday")
                if bday:
                    y = int(str(bday)[0:4])
                    from datetime import datetime
                    age = max(0, datetime.utcnow().year - y)
            except Exception:
                age = 0
            cards.append(PatientCard(
                contact_id=str(c.id),
                patient_user_id=str(c.patient_id),
                full_name=full_name,
                age=age,
                address=pi.get("address") or c.address,
            ))
        return ListPatientsResponse(patients=cards)

    async def detail(self, req: GetContactDetailRequest) -> ContactDetailResponse:
        from uuid import UUID as _UUID
        c = self.repo.get_contact(contact_id=_UUID(req.contact_id))
        if not c:
            raise HTTPException(status_code=404, detail="contact not found")

        payload = c.payload or {}
        mr = payload.get("medical_record") or {}
        diag = payload.get("diagnosis") or None
        # normalize further_test to a list
        ft_raw = payload.get("further_test") or []
        if isinstance(ft_raw, dict):
            ft = ft_raw.get("items") or []
        else:
            ft = ft_raw or []
        reasoning = payload.get("reasoning_process") or None
        todos_raw = payload.get("todos") or []
        conv_raw = payload.get("conversation")

        todos = [TodoItem(text=t.get("text",""), is_check=bool(t.get("is_check"))) for t in todos_raw if t.get("text")]
        conversation = None
        if isinstance(conv_raw, list):
            conversation = [ChatMessageDto(
                id=x.get("id") or "",
                role=x.get("role") or "human",
                content=x.get("content") or "",
                created_at=x.get("created_at"),
            ) for x in conv_raw]

        return ContactDetailResponse(
            contact_id=str(c.id),
            patient_user_id=str(c.patient_id),
            record_id=str(c.record_id),
            address=c.address,
            facility=c.facility,
            medical_record=mr,
            diagnosis=diag,
            reasoning_process=reasoning,
            further_test=ft,
            todos=todos,
            conversation=conversation,
        )

    async def get_messages(self, contact_id: str) -> ContactMessagesResponse:
        from uuid import UUID as _UUID
        rows = self.repo.get_messages(contact_id=_UUID(contact_id))
        return ContactMessagesResponse(messages=[
            ContactMessageDto(
                id=str(r.id),
                role=r.role, content=r.content, created_at=r.created_at
            ) for r in rows
        ])

    async def send_message(self, req: ContactMessageRequest) -> ContactMessageDto:
        from uuid import UUID as _UUID
        sender = self.db.get(User, UUID(req.sender_id))
        role = 'doctor' if (sender and getattr(sender, 'role_type', '') == 'doctor') else 'patient'
        row = self.repo.add_message(contact_id=_UUID(req.contact_id), sender_id=_UUID(req.sender_id), role=role, content=req.content)
        return ContactMessageDto(id=str(row.id), role=row.role, content=row.content, created_at=row.created_at)

    async def my_doctors(self, patient_id: str) -> MyDoctorsResponse:
        rows = self.repo.get_my_doctors(patient_id=UUID(patient_id))
        items = []
        for r in rows:
            items.append({
                'doctor_id': str(r.get('doctor_id')),
                'contact_id': str(r.get('contact_id')),
                'username': r.get('username')
            })
        return MyDoctorsResponse(doctors=items)


