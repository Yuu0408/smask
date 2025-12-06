from typing import List, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


class ReasoningDisease(BaseModel):
    name: str
    likelihood: str = Field(..., description="high | medium | low | rule_out")
    supporting: List[Any] = Field(default_factory=list)
    missing: List[Any] = Field(default_factory=list)
    conflicts: List[Any] = Field(default_factory=list)
    priority: str = Field(
        default="standard", description="must_rule_out | watch | standard"
    )


class DiagnosticReasoningOutput(BaseModel):
    summary: str = Field(..., description="Brief reasoning summary to keep in state.")
    high_priority: List[ReasoningDisease] = Field(default_factory=list)
    differentials: List[ReasoningDisease] = Field(default_factory=list)
    rule_out: List[ReasoningDisease] = Field(default_factory=list)
    recommended_tests: List[str] = Field(default_factory=list, description="Short list of tests or labs to consider.")
    needs_more_questions: bool = Field(
        default=True, description="True when further questions are needed to firm up ranking."
    )
    good_conclusion: bool = Field(
        default=False,
        description="True only when differentials are stable and no high-risk uncertainty remains.",
    )
    refresh_reason: Optional[str] = Field(
        default=None,
        description="If you set needs_more_questions=false but still want re-evaluation later, state why.",
    )


def create_diagnostic_reasoning_chain():
    system = """
You are the INITIAL DIAGNOSTIC REASONING block.
- Use only the compact shared state (symptom_notes, clarified_form, red_flags) to reason.
- Produce a short summary and a ranked set of diseases:
    - high_priority: most likely or high-risk candidates (3-5 max).
    - differentials: other plausible options (up to 5).
    - rule_out: dangerous conditions to exclude.
- Highlight what evidence supports each and what is missing/conflicting. Explicitly check for exposure/context gaps: phơi nhiễm động vật (cắn/cào/dính nước dãi), du lịch, tiếp xúc người bệnh truyền nhiễm, tiêm phòng dại/uốn ván, chấn thương, thuốc ức chế miễn dịch. If absent, list them in missing.
- If red_flags present, ensure those conditions are reflected in high_priority or rule_out.
- Keep text concise to control tokens; avoid repeating the entire state.
- Decide if more questions are needed. Set good_conclusion=true only when you are comfortable ending after rule-out confirmation.
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
        temperature=1,
        # reasoning_effort="none",
    )
    chain = prompt | llm.with_structured_output(DiagnosticReasoningOutput)
    return chain
