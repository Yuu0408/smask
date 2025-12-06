from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import Config
from graph.chains.closing_chain import ClosingOutput, _format_allowed_options
from graph.chains.shared_prompts import PERSONA_TONE_BLOCK


def create_next_step_chain(
    *,
    allowed_addresses: List[str],
    facilities_by_address: Dict[str, List[str]],
):
    addresses_text, facilities_text = _format_allowed_options(
        allowed_addresses, facilities_by_address
    )

    system = PERSONA_TONE_BLOCK + """
You are the NEXT STEP block, called immediately after the FINAL block.
- INPUT: conversation_history (recent turns). Use ONLY this conversation to respond; do not assume any hidden state.
- Never reveal, list, or imply suspected diseases. If asked, remind that only a doctor can confirm and refocus on next actions.
- Keep responses concise, empathetic, and in the patient's language from the conversation.
- Avoid repeating the exact same test list in back-to-back replies; if already shared, acknowledge briefly and move to what is still needed (confirmation or logistics).
- Offer to send the medical record to a doctor. If the patient already answered about including the conversation, respect that choice and avoid re-asking.
- If they agree to send, collect BOTH: address (must be from allowed options) and facility (must be from the options for that address). If they provide an unlisted value, ask them to choose from the provided options.
- When include_conversation, address, and facility are present, set action=SEND_CONTACT and fill send_contact; otherwise set action=NONE and send_contact=null.
- Keep the message compact and actionable.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Conversation history (oldest to newest):\n{conversation_history}\n\n"
                "Allowed addresses: {allowed_addresses}\n"
                "Facilities per address:\n{facilities_by_address}",
            ),
        ]
    ).partial(allowed_addresses=addresses_text, facilities_by_address=facilities_text)

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
    )
    chain = prompt | llm.with_structured_output(ClosingOutput)
    return chain
