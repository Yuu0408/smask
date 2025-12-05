from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


class BasicQuestionOutput(BaseModel):
    question: str = Field(..., description="One clear question to explore a single symptom aspect.")
    options: List[str] = Field(
        default_factory=list, description="0-4 short answer suggestions in patient language."
    )
    target_symptom: str = Field(
        ..., description="Symptom or dimension you are probing (e.g., chest pain location, fever duration)."
    )
    rationale: str = Field(
        ..., description="Why this question matters; name the clinical principle or differential driver."
    )
    red_flags: List[str] = Field(default_factory=list, description="Any immediate red flags detected.")
    info_gaps_closed: List[str] = Field(default_factory=list, description="Which gaps this question aims to close.")
    ready_for_reasoning: bool = Field(
        default=False,
        description="True if core basics are satisfied OR a red flag warrants moving to reasoning.",
    )


def create_basic_questions_chain():
    system = """
You are the MAIN basic-questioning block. Ask principled, focused questions to characterise the chief complaint and core systems, AND actively surface missing context/exposures that could change the differential.
Rules:
- Ask exactly ONE concrete question per turn (no compound questions).
- Prioritise clinical basics: onset/timing, location/radiation, severity, character, progression, triggers/relievers, associated symptoms, functional impact, systemic signs (fever/weight loss), relevant risk factors.
- Explicitly explore context that may be missing from the form when not yet covered: phơi nhiễm (bị chó/mèo/dơi cắn/cào hoặc dính nước dãi), tiêm phòng dại/uốn ván, tiếp xúc người bệnh truyền nhiễm, du lịch gần đây, chấn thương, dùng thuốc/thuốc ức chế miễn dịch. If patient has sốt/đau đầu/khó chịu without cause, ask about phơi nhiễm động vật or tiêm phòng dại first.
- Do NOT repeat a detail already present in symptom_notes or clarified_form unless you need confirmation.
- Never repeat a question that is already in pending_questions or asks the same target as asked_targets; pick a new angle.
- Keep the question short, empathetic, and in the patient's language (use the conversation history in state).
- If you see an immediate red flag, set ready_for_reasoning=true.
- Otherwise, set ready_for_reasoning=true only when essential baseline info feels sufficient for initial reasoning.
- Provide options only when it makes answering easier; keep them short.
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
    chain = prompt | llm.with_structured_output(BasicQuestionOutput)
    return chain
