from typing import List, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


class StateUpdateOutput(BaseModel):
    symptom_notes: List[Any] = Field(
        default_factory=list,
        description="List of new/updated symptom notes with keys: summary, detail?, status?, linked?, onset?, severity?. Strings are also accepted and will be coerced.",
    )
    clarified_form: dict = Field(
        default_factory=dict,
        description="Only the fields clarified by the latest patient message (dot-notation allowed).",
    )
    red_flags: List[str] = Field(default_factory=list, description="Urgent warning signs from the latest message.")
    info_gaps_basic: List[str] = Field(default_factory=list, description="Remaining basic form gaps after this message.")
    info_gaps_symptom: List[str] = Field(default_factory=list, description="Remaining symptom/story gaps.")
    major_change: bool = Field(
        default=False,
        description="True if the message introduces a new key symptom or red flag that should trigger re-reasoning.",
    )


def create_state_update_chain():
    system = """
You are the UPDATE-STATE block.
- Read the latest patient message and the last_question to understand context.
- Produce concise deltas only; do NOT rewrite the whole state.
- symptom_notes should be short summaries; mergeable by text (e.g., "left chest pressure 2h").
- Only include clarified_form entries you can confirm from this message.
- Update info_gaps_* to reflect what is still missing after considering this message.
- Set major_change=true if a red flag or new major symptom appears.
- If the patient clearly says they do not know or are unsure about a question, record that as a symptom_note with status="uncertain" (or a short string), and treat that gap as addressed for now (do NOT keep it in info_gaps_basic or info_gaps_symptom just to force a yes/no later).
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (compact JSON): {state}\nLast asked question: {last_question}\nPatient reply: {patient_message}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(StateUpdateOutput)
    return chain
