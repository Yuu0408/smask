from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config
from graph.chains.shared_prompts import PERSONA_TONE_BLOCK


class RuleOutQuestionOutput(BaseModel):
    question: str = Field(..., description="One question to rule in/out a target disease.")
    options: List[str] = Field(default_factory=list, description="Short answer suggestions if helpful.")
    target_condition: str = Field(..., description="Disease or hypothesis this question targets.")
    rationale: str = Field(..., description="Why this question helps (red flag? key differentiator?).")
    expect_recompute: bool = Field(
        default=True,
        description="True if the answer should trigger re-running reasoning.",
    )
    allow_finish_if_clear: bool = Field(
        default=False,
        description="True if, after this question, we can end if no contradictions arise.",
    )
    selection_intent: Optional[str] = Field(
        default=None,
        description="Echo of the selection intent that led to this question.",
    )
    selection_reason: Optional[str] = Field(
        default=None,
        description="Short reason from selection stage.",
    )


def create_rule_out_in_chain():
    system = PERSONA_TONE_BLOCK + """
You are the RULE-OUT/RULE-IN questioning block.
- You receive the full state for tone/context PLUS a selection_plan that already chose the target condition and intent. Your job is to craft the patient-facing question.
- Follow the selection_plan target_condition and intent; do not switch targets unless it conflicts with asked_targets or pending_questions.
- Target either: (a) dangerous conditions to exclude, (b) highest-probability disease confirmation, or (c) major differentiator between top candidates.
- Ask exactly ONE concise question. No multi-part questions.
- Keep tone empathetic and language consistent with the patient; use conversation_tail/language_hint to stay in-language.
- Use patient_profile (age/gender) when present to keep address and politeness appropriate to the patient; in Vietnamese always include the subject/honorific (anh/chị/bác/em/bạn) and possessive when referring to the patient's body part.
- Only ask about symptoms or observations the patient can answer immediately. Do NOT ask the patient to perform tasks, measurements, or future actions (e.g., do not ask them to take blood pressure or track data).
- Do NOT repeat any question text already in pending_questions or that targets a condition/topic listed in asked_targets.
- If symptom_notes show a status of "uncertain" for a target/symptom, treat it as addressed for now and do not push for a definitive yes/no unless new evidence requires it.
- Only include options if they simplify answering.
- If selection_plan.handoff_to_closing is true, do not ask a new symptom question; instead give a brief, respectful statement acknowledging the request and indicate you'll move to next steps/closing (no multiple-choice).
- Set expect_recompute=true when the answer should trigger re-running reasoning. If you believe one more answer could conclude safely, set allow_finish_if_clear=true.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (JSON, includes conversation_tail for tone): {state}\nSelection plan (JSON): {selection_plan}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(RuleOutQuestionOutput)
    return chain
