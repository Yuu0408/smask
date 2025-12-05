from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


class FormClarificationOutput(BaseModel):
    question: str = Field(
        default="",
        description="One short clarification question about the form. Empty if nothing to ask.",
    )
    options: List[str] = Field(
        default_factory=list,
        description="0-4 short multiple-choice options in the patient's language if helpful.",
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="List of still-missing or unclear fields in dot-notation (e.g., patient_info.gender).",
    )
    clarified_form: dict = Field(
        default_factory=dict,
        description="Only the fields you can confirm or correct based on the latest message.",
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="Critical warning signs surfaced from the latest message.",
    )
    ready_for_basic: bool = Field(
        default=False,
        description="True when form is usable enough to move to basic symptom questioning.",
    )
    rationale: str = Field(
        default="",
        description="Very short note explaining why you asked this question or why you're ready.",
    )


def create_form_clarification_chain():
    system = """
You are a medical intake validator. Work with the compact shared state to ensure the patient form is usable.
- Look at basic_form + clarified_form to avoid repeating already-confirmed items.
- If any critical field is missing or ambiguous, ask ONE concise clarification question focused on the highest priority gap.
- If nothing important is missing, set ready_for_basic=true and leave question="".
- Keep wording empathetic, professional, and in the patient's language (use the conversation history in state for tone).
- Never ask broad symptom questions here; this block is only for form validation/clarification.
- Return only fields you can confidently clarify in clarified_form (do not rewrite the whole form).
- Only include red_flags when the latest user message indicates urgent risk (e.g., chest pain + dyspnea, neuro deficit, severe bleeding).
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (compact JSON): {state}\nLatest patient message (if any): {latest_message}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(FormClarificationOutput)
    return chain
