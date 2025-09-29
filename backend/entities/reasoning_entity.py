from pydantic import BaseModel, Field
from typing import List, Optional

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
