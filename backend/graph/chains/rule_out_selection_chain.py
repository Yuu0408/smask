from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config
from graph.chains.shared_prompts import PERSONA_TONE_BLOCK


class RuleOutSelectionOutput(BaseModel):
    target_condition: str = Field(..., description="Disease/hypothesis to rule in/out next.")
    intent: str = Field(
        ...,
        description="One of: danger_rule_out | confirm_top | differentiate | fill_missing_info",
    )
    reason: str = Field(..., description="Why this target was chosen (short).")
    allow_finish_if_clear: bool = Field(
        default=False,
        description="If true, after this answer we can finish if no contradictions arise.",
    )
    expect_recompute: bool = Field(
        default=True,
        description="True if answering this should trigger re-running reasoning.",
    )
    handoff_to_closing: bool = Field(
        default=False,
        description="Set true when the patient requests to conclude/diagnose now or decline more questions; signal to skip further rule-out questions and move to closing if safe.",
    )
    skip_questions: List[str] = Field(
        default_factory=list,
        description="Short phrases for questions/targets that should NOT be asked again given asked_targets, pending_questions, and conversation_tail.",
    )


def create_rule_out_selection_chain():
    system = PERSONA_TONE_BLOCK + """
You are the QUESTION-SELECTION block between diagnostic reasoning and patient questioning.
- INPUT: compact state (reasoning_snapshot, symptom_notes, asked_targets, pending_questions, info_gaps_symptom, red_flags, last_question, patient_profile, selection_plan, conversation_tail).
- TASK: choose the single best target_condition to ask about next, following priority:
  1) Dangerous conditions that must be ruled out.
  2) Highest-probability condition confirmation.
  3) Major differentiator between top candidates.
  4) High-value missing info (info_gaps_symptom) not already asked.
- DO NOT repeat targets already in asked_targets or pending_questions unless new info demands clarification; if a symptom/target is marked uncertain, treat it as addressed for now.
- Populate skip_questions with concise question/target phrases that are already covered (asked_targets, pending_questions, or clearly answered in conversation_tail) so downstream blocks avoid repeating them.
- If the conversation_tail shows the patient is asking for something else (e.g., wants diagnosis or asks to stop), prioritize that intent: set handoff_to_closing=true when safe, or pick one single high-yield safety/triage question with allow_finish_if_clear=true.
- Keep selection concise; no question wording here, just pick the target/intention.
- Set allow_finish_if_clear=true only if one more answer could safely conclude.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Compact state JSON: {state}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(RuleOutSelectionOutput)
    return chain
