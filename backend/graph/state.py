from typing import List, Optional
from typing_extensions import TypedDict
from entities.medical_record_entity import MedicalRecord
from entities.predicted_diseases_entity import DiagnosisPaper, DiagnosisResponse

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