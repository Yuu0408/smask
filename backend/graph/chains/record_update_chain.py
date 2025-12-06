from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config
from graph.chains.shared_prompts import PERSONA_TONE_BLOCK


class RecordUpdateOutput(BaseModel):
    record_updates: dict = Field(
        default_factory=dict,
        description=(
            "Partial medical record payload to merge (e.g., patient_info, medical_history, social_information, "
            "obstetric_gynecological_history). Include only fields you can confirm from the conversation or reasoning."
        ),
    )
    summary_note: str = Field(
        default="",
        description="Optional short note for the record about key confirmed info or clarifications.",
    )


def create_record_update_chain():
    system = PERSONA_TONE_BLOCK + """
You are the MEDICAL RECORD UPDATE block, called right before the final next-step message.
- INPUT: shared state (basic_form, clarified_form, symptom_notes, reasoning_snapshot, conversation_tail, patient_profile, selection_plan).
- OUTPUT: record_updates containing only fields you can confidently add or correct in the medical record:
  - patient_info.*
  - medical_history.* (chief_complaint, medical_history, past_medical_history, current_medications, allergies, family_medical_history)
  - social_information.*
  - obstetric_gynecological_history.*
- Do NOT invent or guess values. If unsure, leave the field out.
- Do NOT repeat existing values unless you are correcting them with higher confidence.
- Keep summary_note brief and only if helpful.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (JSON): {state}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(RecordUpdateOutput)
    return chain
