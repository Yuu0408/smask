# app/models/entities/model.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID as PyUUID, uuid4
import uuid

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, JSON, PrimaryKeyConstraint, String, Boolean, Integer
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
# If you're on Postgres and want native UUID + FK, you can optionally use:
# from sqlalchemy.dialects.postgresql import UUID as pgUUID

# --- Base schemas (Pydantic-style) ---

class MedicalRecordBase(SQLModel):
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw form payload")


class MedicalRecordCreate(MedicalRecordBase):
    user_id: PyUUID


class MedicalRecordRead(MedicalRecordBase):
    record_id: PyUUID
    user_id: PyUUID
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )


# --- DB model ---

class MedicalRecord(MedicalRecordBase, table=True):
    __tablename__ = "medical_records"

    # Primary key
    record_id: PyUUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        # If you want DB-generated UUID on Postgres instead of Python:
        # sa_column=Column(pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )

    # Owner of the record
    user_id: PyUUID = Field(
        foreign_key="users.id",  # adapt to your actual users table/column
        index=True,
        nullable=False,
    )

    # Flexible form data as JSON
    data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
    )

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )

    # If you later add a relationship:
    # user: Optional["User"] = Relationship(back_populates="medical_records")

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,  # PK goes here
            server_default=text("gen_random_uuid()"),
        ),
    )
    username: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    role_type: str = Field(sa_column=Column(String(50), nullable=False, server_default="patient"))  # "patient" | "doctor"
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
        description="Additional user metadata",
    )
    is_active: bool = Field(sa_column=Column(Boolean, nullable=False, server_default="1"))
    token_version: int = Field(sa_column=Column(Integer, nullable=False, server_default="0"))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

class ChatHistory(SQLModel, table=True):
    __tablename__ = "chat_history"

    id: PyUUID = Field(default_factory=uuid4, primary_key=True, index=True)
    record_id: PyUUID = Field(foreign_key="medical_records.record_id", index=True)
    user_id: PyUUID = Field(index=True)
    role: str                           # "user" | "ai" | "system"
    content: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )

class AIStateBase(SQLModel):
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw form payload")

class AIState(AIStateBase, table=True):
    __tablename__ = "ai_state"
    __table_args__ = (
        PrimaryKeyConstraint("record_id", "user_id", name="pk_ai_state"),
    )

    record_id: PyUUID = Field(foreign_key="medical_records.record_id", index=True)
    user_id: PyUUID = Field(index=True)
    data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
    )

# --- TODO model ---
class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: PyUUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: PyUUID = Field(foreign_key="users.id", index=True)
    record_id: PyUUID = Field(foreign_key="medical_records.record_id", index=True)
    text: str = Field(sa_column=Column(String(1024), nullable=False))
    is_check: bool = Field(sa_column=Column(Boolean, nullable=False, server_default="0"))
    position: int = Field(sa_column=Column(Integer, nullable=False, server_default="0"))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )

# --- Diagnosis model ---
class Diagnosis(SQLModel, table=True):
    __tablename__ = "diagnoses"

    id: PyUUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: PyUUID = Field(foreign_key="users.id", index=True)
    record_id: PyUUID = Field(foreign_key="medical_records.record_id", index=True)
    reasoning_process: str = Field(sa_column=Column(String(4096), nullable=False))
    diagnosis: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False, server_default="{}"))
    further_test: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False, server_default="{}"))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
