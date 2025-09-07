from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


# --- Nested payload models ---

class PatientInfo(BaseModel):
    full_name: str
    birthday: date  # parses "YYYY-MM-DD" strings
    gender: Literal["Male", "Female", "Other"]
    occupation: str
    nationality: str
    address: str


class MedicalHistory(BaseModel):
    chief_complaint: str
    medical_history: str
    past_medical_history: str
    current_medications: str
    allergies: str
    family_medical_history: str


class SocialInformation(BaseModel):
    alcohol_consumption: str
    smoking_habit: str
    living_situation: str
    daily_activity_independence: str
    recent_travel_history: str


class ObstetricGynecologicalHistory(BaseModel):
    menstruation_status: str
    menstrual_cycle: str
    recent_sexual_activity: Optional[bool] = None


class MedicalRecordData(BaseModel):
    patient_info: PatientInfo
    medical_history: MedicalHistory
    social_information: SocialInformation
    obstetric_gynecological_history: Optional[ObstetricGynecologicalHistory] = None

    # Optional rule: if gender is Female, require obstetric_gynecological_history
    @model_validator(mode="after")
    def validate_ob_history_if_needed(self):
        if (
            self.patient_info.gender == "Female"
            and self.obstetric_gynecological_history is None
        ):
            raise ValueError(
                "obstetric_gynecological_history is required when gender is Female"
            )
        return self


# --- Request/Response DTOs ---

class AddMedicalRecordRequest(BaseModel):
    user_id: UUID = Field(..., description="Owner of the medical record")
    data: MedicalRecordData


class AddMedicalRecordResponse(BaseModel):
    message: str
    record_id: str
    created_at: datetime
    updated_at: datetime

class ChatMessageDto(BaseModel):
    id: str
    role: Literal["human", "ai", "system"]
    content: str
    created_at: datetime

class GetChatHistoryRequest(BaseModel):
    user_id: str
    record_id: str

class GetChatHistoryResponse(BaseModel):
    history: List[ChatMessageDto]

class AIStateData(BaseModel):
    reasoning: str
    note: str
    decision: str

class ChatTextRequest(BaseModel):
    user_id: str
    record_id: str
    message: str

class ChatTextResponse(BaseModel):
    message: str
    multiple_choices: Optional[List[str]] = None