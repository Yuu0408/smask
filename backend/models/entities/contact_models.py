from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID as PyUUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func, JSON, String, Boolean, UniqueConstraint


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("patient_id", "record_id", name="uq_contact_patient_record"),
    )

    id: PyUUID = Field(default_factory=uuid4, primary_key=True, index=True)
    # Patient who initiated the contact
    patient_id: PyUUID = Field(foreign_key="users.id", index=True)
    # Optional doctor assigned after first reply
    assigned_doctor_id: Optional[PyUUID] = Field(default=None, foreign_key="users.id", index=True)
    # Link back to medical record
    record_id: PyUUID = Field(foreign_key="medical_records.record_id", index=True)

    address: str = Field(sa_column=Column(String(255), nullable=False))
    facility: str = Field(sa_column=Column(String(255), nullable=False))

    include_conversation: bool = Field(sa_column=Column(Boolean, nullable=False, server_default="0"))

    # Snapshot payload for convenience: medical_record, diagnosis, todo, conversation
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )


class ContactMessage(SQLModel, table=True):
    __tablename__ = "contact_messages"

    id: PyUUID = Field(default_factory=uuid4, primary_key=True, index=True)
    contact_id: PyUUID = Field(foreign_key="contacts.id", index=True)
    sender_id: PyUUID = Field(foreign_key="users.id", index=True)
    # 'doctor' | 'patient'
    role: str = Field(sa_column=Column(String(50), nullable=False))
    content: str = Field(sa_column=Column(String(4096), nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
