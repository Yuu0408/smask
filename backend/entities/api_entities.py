from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from entities.medical_record_entity import MedicalRecord
from entities.predicted_diseases_entity import DiagnosisPaper, DiagnosisResponse
from datetime import date

class PatientInfo(BaseModel):
    full_name: str
    birthday: date  # Assuming ISO 8601 date string; convert to `date` type later if needed
    gender: str
    occupation: str
    nationality: str

class SocialInformation(BaseModel):
    alcohol_consumption: Optional[str]
    smoking_habit: Optional[str]
    living_situation: Optional[str]
    daily_activity_independence: Optional[str]
    recent_travel_history: Optional[str]

class ObstetricGynecologicalHistory(BaseModel):
    menstruation_status: Optional[str]
    menstrual_cycle: Optional[str]
    recent_sexual_activity: Optional[bool]

class MedicalRecordRequest(BaseModel):
    patient_info: PatientInfo
    chief_complaint: str
    social_information: SocialInformation
    obstetric_gynecological_history: Optional[ObstetricGynecologicalHistory] = None

class ConversationRequest(BaseModel):
    session_id: UUID
    user_message: str

class GraphState(TypedDict):
    todo: Optional[List[str]] = None
    diagnosis_paper: DiagnosisPaper
    note: str = ""
    reasoning: str = ""
    history: str = ""
    decision: str = "CONVERSATION"  # Default starting point
    medical_record: MedicalRecord
    diagnosis_response: DiagnosisResponse
    additional_info: str = ""
    follow_up_questions: Optional[List[str]] = None
    previous_state: str = "CONVERSATION"

class ConversationResponse(BaseModel):
    ai_response: str
    state: GraphState
    multiple_choices: List[str]