from typing import Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config import Config


class ClosingOutput(BaseModel):
    message: str = Field(..., description="Concise closing message to the patient.")
    options: List[str] = Field(default_factory=list, description="Optional quick replies in patient language.")
    recommendation: str = Field(
        default="",
        description="Short recommendation summary (tests, next steps, or safety advice) for state tracking.",
    )
    action: str = Field(
        default="NONE",
        description="Action to take. One of: NONE, SEND_CONTACT",
    )
    send_contact: Optional[Dict] = Field(
        default=None,
        description=(
            "If action is SEND_CONTACT, provide an object: "
            "{include_conversation: boolean, address: string, facility: string}. "
            "Address and facility must be chosen ONLY from the provided options."
        ),
    )


def _format_allowed_options(allowed_addresses: List[str], facilities_by_address: Dict[str, List[str]]):
    addr_text = ", ".join(allowed_addresses) if allowed_addresses else "(none)"
    lines = []
    for addr in allowed_addresses:
        facs = facilities_by_address.get(addr) or []
        if facs:
            lines.append(f"{addr}: " + ", ".join(facs))
        else:
            lines.append(f"{addr}: (no facilities)")
    fac_text = "\n".join(lines) if lines else "(none)"
    return addr_text, fac_text


def create_closing_chain(
    *,
    allowed_addresses: List[str],
    facilities_by_address: Dict[str, List[str]],
):
    addresses_text, facilities_text = _format_allowed_options(allowed_addresses, facilities_by_address)

    system = """
You are finishing the diagnostic conversation as the FINAL NEXT-STEP block.
- Never reveal, list, or imply suspected diseases or diagnoses. If asked, state that only a doctor can confirm and focus on what to do next.
- Provide a concise closing message that clearly states next steps: recommended tests, when to seek in-person/urgent care, and how the patient can proceed. Lean on recommended_tests or other action items in the shared state.
- Use the patient's language from the conversation history in state; stay empathetic and easy to follow.
- Offer to send the medical record to a doctor. Ask if they want to include the conversation history.
- If the patient agrees, collect BOTH:
    1) address (must be one of the allowed values)
    2) facility (must be one of the options for the chosen address)
- If they give an unlisted value, politely ask them to pick from the provided options.
- When you have include_conversation, address, and facility, set action=SEND_CONTACT and fill send_contact accordingly; otherwise use action=NONE and send_contact=null.
- Keep the message compact; avoid long explanations.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Shared state (compact JSON): {state}\nReasoning snapshot: {reasoning_snapshot}\nAllowed addresses: {allowed_addresses}\nFacilities per address:\n{facilities_by_address}",
            ),
        ]
    ).partial(allowed_addresses=addresses_text, facilities_by_address=facilities_text)

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(ClosingOutput)
    return chain
