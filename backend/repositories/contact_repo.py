from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.entities.contact_models import Contact, ContactMessage
from models.entities.model import User
from repositories.medical_record_repo import MedicalRecordRepo
from repositories.chat_history_repo import ChatHistoryRepo
from repositories.todo_repo import TodoRepo
from repositories.diagnosis_repo import DiagnosisRepo


class ContactRepo:
    def __init__(self, db: Session):
        self.db = db
        self.med = MedicalRecordRepo(db)
        self.chat = ChatHistoryRepo(db)
        self.todo = TodoRepo(db)
        self.diag = DiagnosisRepo(db)

    def create_contact(self, *, patient_id: UUID, record_id: UUID, address: str, facility: str, include_conversation: bool) -> Contact:
        try:
            # Prevent duplicate sends for the same record by the same patient
            exists_stmt = select(Contact).where(
                Contact.patient_id == patient_id,
                Contact.record_id == record_id,
            )
            existing = self.db.exec(exists_stmt).first()
            if existing:
                raise HTTPException(status_code=409, detail="This medical record has already been sent")

            record = self.med.get_medical_record_by_id(record_id=record_id, user_id=patient_id)
            latest_diag = self.diag.get_latest(user_id=patient_id, record_id=record_id)
            todos = self.todo.list_todos(user_id=patient_id, record_id=record_id)
            history = self.chat.get_chat_history(user_id=patient_id, record_id=record_id) if include_conversation else []

            payload: Dict[str, Any] = {
                "medical_record": record.data,
                "diagnosis": getattr(latest_diag, "diagnosis", None) if latest_diag else None,
                "further_test": getattr(latest_diag, "further_test", None) if latest_diag else None,
                "reasoning_process": getattr(latest_diag, "reasoning_process", None) if latest_diag else None,
                "todos": [
                    {"text": t.text, "is_check": bool(t.is_check)} for t in todos if t.text
                ],
                "conversation": [
                    {"id": str(h.id), "role": h.role, "content": h.content, "created_at": h.created_at.isoformat()}
                    for h in history
                ] if include_conversation else None,
            }

            row = Contact(
                patient_id=patient_id,
                record_id=record_id,
                address=address,
                facility=facility,
                include_conversation=include_conversation,
                payload=payload,
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except IntegrityError as e:
            # Unique constraint violation (edge case race condition)
            self.db.rollback()
            raise HTTPException(status_code=409, detail="This medical record has already been sent") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create contact") from e

    def list_for_doctor(self, *, doctor_id: UUID) -> List[Contact]:
        try:
            doc = self.db.get(User, doctor_id)
            if not doc or doc.role_type != "doctor":
                raise HTTPException(status_code=400, detail="Invalid doctor")
            meta = doc.user_metadata or {}
            addr = meta.get("address")
            fac = meta.get("facility")
            if not addr or not fac:
                return []
            stmt = select(Contact).where(Contact.address == addr, Contact.facility == fac).order_by(Contact.created_at.desc())
            return self.db.exec(stmt).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="DB error listing contacts") from e

    def get_contact(self, *, contact_id: UUID) -> Optional[Contact]:
        return self.db.get(Contact, contact_id)

    def get_messages(self, *, contact_id: UUID) -> List[ContactMessage]:
        try:
            stmt = select(ContactMessage).where(ContactMessage.contact_id == contact_id).order_by(ContactMessage.created_at.asc())
            return self.db.exec(stmt).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="DB error fetching messages") from e

    def add_message(self, *, contact_id: UUID, sender_id: UUID, role: str, content: str) -> ContactMessage:
        try:
            row = ContactMessage(contact_id=contact_id, sender_id=sender_id, role=role, content=(content or "").strip())
            if not row.content:
                raise HTTPException(status_code=400, detail="Message content cannot be empty")
            self.db.add(row)
            # assign doctor if first doctor message and none yet
            contact = self.get_contact(contact_id=contact_id)
            if role == "doctor" and contact and not contact.assigned_doctor_id:
                contact.assigned_doctor_id = sender_id
                self.db.add(contact)
            self.db.commit()
            self.db.refresh(row)
            return row
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="DB error adding message") from e

    
    def get_my_doctors(self, *, patient_id: UUID) -> list[dict]:
        try:
            # collect latest contact per doctor
            stmt = select(Contact).where(Contact.patient_id == patient_id, Contact.assigned_doctor_id.is_not(None)).order_by(Contact.created_at.desc())
            rows = self.db.exec(stmt).all()
            latest_by_doctor: dict[UUID, UUID] = {}
            for c in rows:
                if not c.assigned_doctor_id:
                    continue
                if c.assigned_doctor_id not in latest_by_doctor:
                    latest_by_doctor[c.assigned_doctor_id] = c.id
            if not latest_by_doctor:
                return []
            stmt2 = select(User).where(User.id.in_(list(latest_by_doctor.keys())))
            users = self.db.exec(stmt2).all()
            result = []
            for u in users:
                result.append({
                    'doctor_id': u.id,
                    'username': u.username,
                    'contact_id': latest_by_doctor.get(u.id),
                })
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail='DB error fetching doctors') from e
