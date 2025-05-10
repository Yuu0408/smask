from pydantic import BaseModel, Field
from typing import List, Optional

from entities.medical_record_entity import MedicalRecord

class Diagnosis(BaseModel):
    class PredictedDisease(BaseModel):
        name: str = Field(..., description="The name of the diagnosed or predicted disease.")
        supporting_evidence: List[str] = Field(..., description="List of symptoms and diagnostic results supporting the diagnosis.")
        differentiating_factor: Optional[str] = Field(None, description="Key factor that differentiates this disease from others.")
        search_keywords: List[str] = Field(..., description="List of questions to ask internet to confirm / reconsider the predicted disease.")

    most_likely: Optional[PredictedDisease] = Field(
        None, description="The condition most strongly supported by the patient's symptoms and history."
    )
    
    possible_diagnoses: List[PredictedDisease] = Field(
        [], description="Up to 6 other plausible diagnoses that may explain the patient's symptoms."
    )
    
    rule_out: List[PredictedDisease] = Field(
        [], description="Dangerous or serious conditions that might not fully match the case but must be ruled out carefully due to risk."
    )

class FurtherTest(BaseModel):
    name: str = Field(..., description="The name of the test")
    purpose: str = Field(..., description="Why the test is needed")
    related_condition: List[str] = Field(..., description="Conditions or symptoms this test addresses")
    urgency: Optional[str] = Field(..., description="Urgency of the test: immediate, urgent, routine, etc.")

class DiagnosisResponse(BaseModel):
    # generation: str = Field(..., description="What you would tell the patient after diagnosis")
    todo: Optional[List[str]] = Field(description="List of things patient should do (further test, things to do,...) in detailed. Must be writen in the same language as the conversation between patient.")
    medical_record: Optional[MedicalRecord] = Field(None, description="Your updated completed medical record based on the conversation between patient. The medical record content should be in the same language with the conversation with patient. You may need to translate the the medical record content to the same language with the conversation with patient")
    reasoning_process: str = Field(..., description="Your reasoning process")
    diagnosis: Diagnosis = Field(..., description="Categorized potential conditions based on likelihood and differentiating factors.")
    further_test: List[FurtherTest] = Field(..., description="Detailed recommended further tests with purpose and urgency")
    # further_question_to_ask: Optional[List[str]] = Field(None, description="Further questions to ask patient in order to rule out / reconsider diseases. Not return anything if there is no need to ask further questions")

class DiagnosisPaper(BaseModel):
    reasoning_process: str = Field(..., description="Your reasoning process")
    diagnosis: Diagnosis = Field(..., description="Categorized potential conditions based on likelihood and differentiating factors.")
    further_test: List[FurtherTest] = Field(..., description="Detailed recommended further tests with purpose and urgency")