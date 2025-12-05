from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


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


def create_rule_out_in_chain():
    system = """
You are the RULE-OUT/RULE-IN questioning block.
- Use the latest reasoning_snapshot and symptom notes to pick the single best next question.
- Target either: (a) dangerous conditions to exclude, (b) highest-probability disease confirmation, or (c) major differentiator between top candidates.
- Ask exactly ONE concise question. No multi-part questions.
- Keep tone empathetic and language consistent with the conversation history in state.
- Only ask about symptoms or observations the patient can answer immediately. Do NOT ask the patient to perform tasks, measurements, or future actions (e.g., do not ask them to take blood pressure or track data).
- Do NOT repeat any question text already in pending_questions or that targets a condition/topic listed in asked_targets.
- Only include options if they simplify answering.
- Set expect_recompute=true when the answer should trigger re-running reasoning. If you believe one more answer could conclude safely, set allow_finish_if_clear=true.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (compact JSON, includes full conversation history): {state}",
            ),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(RuleOutQuestionOutput)
    return chain
