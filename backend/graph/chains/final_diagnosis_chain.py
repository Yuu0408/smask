from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config
from graph.chains.shared_prompts import PERSONA_TONE_BLOCK


class DiagnosisDisease(BaseModel):
    name: str = Field(..., description="Disease or condition name.")
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence or symptoms supporting this condition.",
    )
    differentiating_factor: Optional[str] = Field(
        default=None,
        description="Key factor that separates this from other options.",
    )


class DiagnosisBundle(BaseModel):
    most_likely: Optional[DiagnosisDisease] = Field(
        default=None,
        description="The single most likely condition, if any.",
    )
    possible_diagnoses: List[DiagnosisDisease] = Field(
        default_factory=list,
        description="Other plausible diagnoses.",
    )
    rule_out: List[DiagnosisDisease] = Field(
        default_factory=list,
        description="Serious conditions to rule out.",
    )


class FurtherTest(BaseModel):
    name: str = Field(..., description="Test or imaging name.")
    purpose: str = Field(..., description="Why this test is needed.")
    related_condition: List[str] = Field(
        default_factory=list,
        description="Conditions or symptoms this test addresses.",
    )
    urgency: Optional[str] = Field(
        default=None,
        description="Urgency such as immediate, urgent, or routine.",
    )


class FinalDiagnosisOutput(BaseModel):
    reasoning_process: str = Field(
        ...,
        description="Concise clinician-facing summary of the diagnostic reasoning.",
    )
    diagnosis: DiagnosisBundle = Field(
        ...,
        description="Structured diagnosis object for the patient detail page.",
    )
    further_test: List[FurtherTest] = Field(
        default_factory=list,
        description="Recommended tests or follow-ups.",
    )


def create_final_diagnosis_chain():
    system = PERSONA_TONE_BLOCK + """
You are the FINAL DIAGNOSIS block, called after the conversation and record updates.
- INPUT: shared state (clarified_form, symptom_notes, reasoning_snapshot, conversation_tail, patient_profile).
- OUTPUT: clinician-facing reasoning + structured diagnosis for the patient detail page.
- Keep wording concise and clinical; do NOT address the patient directly.
- Use reasoning_snapshot to back up the diagnosis. If data is missing, leave lists empty instead of inventing.
- Provide further tests only when relevant; keep names and purposes short.
- Maintain the conversation language if clearly indicated by the state.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Shared state (JSON): {state}"),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(FinalDiagnosisOutput)
    return chain
