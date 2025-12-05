from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import List, Optional, Literal, Set
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


class AlcoholDetails(BaseModel):
    per_month_times: Optional[int] = None
    per_week_times: Optional[int] = None
    per_time_ml: Optional[int] = None
    avg_per_day_ml: Optional[int] = None
    drink_type: Optional[str] = None


class SmokingDetails(BaseModel):
    start_age: Optional[int] = None
    end_age: Optional[int] = None
    cigarettes_per_day: Optional[int] = None
    years_smoked: Optional[int] = None


class SocialInformation(BaseModel):
    alcohol_consumption: str
    alcohol_details: Optional[AlcoholDetails] = None
    smoking_habit: str
    smoking_details: Optional[SmokingDetails] = None
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

class Reasoning(BaseModel):
    class PredictedDisease(BaseModel):
        name: str = Field(..., description="The name of the diagnosed or predicted disease.")
        symptoms: List[str] = Field(..., description="List of symptoms associated with the disease.")
        supporting_evidence: List[str] = Field(..., description="List of symptoms you can tell from patient that supports the diagnosis.")
        differentiating_factor: Optional[str] = Field(None, description="Key factor that differentiates this disease from others.")

    most_likely: Optional[PredictedDisease] = Field(
        None, description="The condition most strongly supported by the patient's symptoms and history."
    )
    
    possible_diagnoses: List[PredictedDisease] = Field(
        [], description="Other plausible diagnoses that may explain the patient's symptoms."
    )
    
    rule_out: List[PredictedDisease] = Field(
        [], description="Dangerous or serious conditions that might not fully match the case but must be ruled out carefully due to risk."
    )

class SymptomNote(BaseModel):
    summary: str = Field(..., description="Short sentence describing the symptom in patient language.")
    detail: Optional[str] = Field(None, description="Optional expansion or qualifiers.")
    status: Literal["reported", "confirmed", "ruled_out", "uncertain"] = "reported"
    source: Literal["patient", "assistant"] = "patient"
    linked: List[str] = Field(default_factory=list, description="Diseases or systems this symptom relates to.")
    onset: Optional[str] = None
    severity: Optional[str] = None


class ReasoningCandidate(BaseModel):
    name: str
    likelihood: Literal["high", "medium", "low", "rule_out"] = "medium"
    supporting: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    priority: Literal["must_rule_out", "watch", "standard"] = "standard"


class ReasoningSnapshot(BaseModel):
    summary: str
    high_priority: List[ReasoningCandidate] = Field(default_factory=list)
    differentials: List[ReasoningCandidate] = Field(default_factory=list)
    rule_out: List[ReasoningCandidate] = Field(default_factory=list)
    recommended_tests: List[str] = Field(default_factory=list)
    needs_more_questions: bool = True
    good_conclusion: bool = False
    refresh_reason: Optional[str] = None


class PendingQuestion(BaseModel):
    id: str
    text: str
    options: List[str] = Field(default_factory=list)
    target: Optional[str] = None
    intent: Literal["clarify_form", "basic_symptom", "rule_out", "conclusion"] = "basic_symptom"
    rationale: Optional[str] = None


class SharedState(BaseModel):
    basic_form: dict = Field(default_factory=dict, description="Original patient form payload.")
    clarified_form: dict = Field(default_factory=dict, description="Only fields clarified or corrected during chat.")
    symptom_notes: List[SymptomNote] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    info_gaps_basic: List[str] = Field(default_factory=list)
    info_gaps_symptom: List[str] = Field(default_factory=list)
    reasoning_snapshot: Optional[ReasoningSnapshot] = None
    pending_questions: List[PendingQuestion] = Field(default_factory=list)
    last_question: Optional[PendingQuestion] = None
    asked_targets: List[str] = Field(default_factory=list, description="Targets/topics already asked to avoid repeats.")
    conversation_tail: List[dict] = Field(default_factory=list, description="Full conversation history to preserve context and tone.")


class AIStateData(BaseModel):
    shared_state: SharedState
    stage: Literal["FORM_CLARIFICATION", "BASIC_QUESTIONING", "REASONING", "RULE_OUT", "CLOSING"]

class ChatTextRequest(BaseModel):
    user_id: str
    record_id: str
    message: str

class ChatTextResponse(BaseModel):
    message: str
    multiple_choices: Optional[List[str]] = None
    decision: Optional[str] = None
    action: Optional[str] = None
    send_contact: Optional[dict] = None
    todos: Optional[List[TodoItem]] = None


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None


class UserPublic(BaseModel):
    id: str
    record_id: str
    username: str
    is_active: bool
    role: Literal["patient", "doctor"]

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    accessToken: str
    user: UserPublic

class RegisterRequest(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=128)
    role: Literal["patient", "doctor"] = "patient"
    metadata: Optional[dict] = None

class GetCurrentRecordRequest(BaseModel):
    user_id: Optional[str] = None
    record_id: Optional[str] = None

class GetCurrentRecordResponse(BaseModel):
    user_id: str
    record_id: str
    created_at: datetime
    updated_at: datetime
    data: MedicalRecordData

class GetAllChatHistoryRequest(BaseModel):
    user_id: str

# --- TODO DTOs ---
class GetCurrentTodoRequest(BaseModel):
    user_id: Optional[str] = None
    record_id: Optional[str] = None

class TodoItem(BaseModel):
    text: str
    is_check: bool = False

class GetCurrentTodoResponse(BaseModel):
    user_id: str
    record_id: str
    items: List[TodoItem]

class UpdateTodoItemRequest(BaseModel):
    user_id: str
    record_id: Optional[str] = None
    index: int
    is_check: bool

class UpdateTodoItemResponse(GetCurrentTodoResponse):
    pass

# --- Contact DTOs ---
class SendContactRequest(BaseModel):
    user_id: str
    record_id: str
    include_conversation: bool
    address: str
    facility: str

class SendContactResponse(BaseModel):
    ok: bool
    contact_id: str

class PatientCard(BaseModel):
    contact_id: str
    patient_user_id: str
    full_name: str
    age: int
    address: str

class ListPatientsRequest(BaseModel):
    doctor_id: str

class ListPatientsResponse(BaseModel):
    patients: List[PatientCard]

class GetContactDetailRequest(BaseModel):
    contact_id: str

class ContactDetailResponse(BaseModel):
    contact_id: str
    patient_user_id: str
    record_id: str
    address: str
    facility: str
    medical_record: MedicalRecordData | dict
    diagnosis: Optional[dict] = None
    reasoning_process: Optional[str] = None
    further_test: Optional[list] = None
    todos: List[TodoItem] = []
    conversation: Optional[List[ChatMessageDto]] = None

class ContactMessageRequest(BaseModel):
    contact_id: str
    sender_id: str
    content: str

class ContactMessageDto(BaseModel):
    id: str
    role: Literal["doctor", "patient"]
    content: str
    created_at: datetime

class ContactMessagesResponse(BaseModel):
    messages: List[ContactMessageDto]

class MyDoctor(BaseModel):
    doctor_id: str
    contact_id: str
    username: str
    
class MyDoctorsResponse(BaseModel):
    doctors: List[MyDoctor]

