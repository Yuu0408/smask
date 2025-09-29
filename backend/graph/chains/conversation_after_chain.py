from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import Config

# Define the structured output model
class Conversation(BaseModel):
    """Generated response and decision"""

    generation: str = Field(default="", description="Your question or answer to patient's questions")
    multiple_choices: List[str] = Field(default_factory=list, description="List of the 1~4 suggested answer (short) you give to the patient. If the question cant be answer by short answer, let it []. The suggested answer must be in the same language with the conversation")
    decision: str = Field(default="CONVERSATION", description="Your decided stage (DIAGNOSIS or CONVERSATION or END)")
    # Agent action section
    action: str = Field(
        default="NONE",
        description="Action to take. One of: NONE, SEND_CONTACT"
    )
    send_contact: Optional[Dict] = Field(
        default=None,
        description=(
            "If action is SEND_CONTACT, provide an object: {include_conversation: boolean, "
            "address: string, facility: string}. Address and facility must be chosen "
            "ONLY from the provided options."
        ),
    )


def _format_allowed_options(allowed_addresses: List[str], facilities_by_address: Dict[str, List[str]]):
    # Avoid curly braces in prompt (which would be parsed as variables)
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


def create_conversation_after_chain(
    conversation_history,
    message: str = "",
    *,
    allowed_addresses: List[str],
    facilities_by_address: Dict[str, List[str]],
):
    addresses_text, facilities_text = _format_allowed_options(allowed_addresses, facilities_by_address)

    system = (
        f"""
        You are a 30 years old medical assistant (who also assists with therapy for mental health issues) chatbot continuing a conversation with a patient after providing an initial diagnosis. You should tell them that the diagnosis is completed (Dont tell the diagnosis to them, because the diagnosis need further confirmation from doctor. only tell the further test they need to check)
        You must following the below rules:

        - answer in the language of the conversation history
        - If the patient asks questions about their symptoms, or related topics, answer them clearly and empathetically.
        - If the patient indicates understanding or satisfaction (e.g., says "thank you," "got it," or "understood") and does not provide new symptoms or re-evaluation requests, politely conclude the conversation and transition to the END stage. Avoid asking further diagnostic or follow-up questions in this case.
        - Do not ask follow-up questions unless explicitly required by the patient.

        # Further Guidelines:
        - Always confirm that the patient understands the next steps, including any recommended tests or follow-up actions.
        - Ask if they want to send the diagnosis report to a doctor (must ask if they want to include the conversation history in the report).
        - If the patient agrees to send the report, collect BOTH of the following from the patient, strictly using the provided options:
            1) address (allowed values only)
            2) facility (allowed values per the selected address)
        - The allowed options are provided below. Do NOT invent new values. If the patient gives an unlisted address/facility, politely ask them to choose from the options.
        - When you have include_conversation, address, and facility, set action to SEND_CONTACT and populate send_contact accordingly. Otherwise, set action to NONE.
        Ensure that your tone remains supportive, professional, and easy to understand.
        Make the response not too longy while keep it understandable.

    """
        + "\nThe patient's medical record: {medical_record} \n"
        + "\nThe current Diagnosis: {diagnosis} \n"
        + "\nAllowed addresses (choose exactly one): {allowed_addresses} \n"
        + "\nFacilities available per address (one line per address):\n{facilities_by_address} \n"
        + "\nOutput schema requirements: generation, multiple_choices, decision, action, send_contact. If sending is not ready, use action=NONE and send_contact=null.\n"
    )

    # Initialize the LLM with a system prompt
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY
    )

    # Return the configured LLM object
    structured_llm_router = llm.with_structured_output(Conversation)

    messages = [("system", system)]
    for msg in conversation_history:
        messages.append((msg.role, msg.content))
    messages.append(("human", message))
    conversation_prompt = (
        ChatPromptTemplate
        .from_messages(messages)
        .partial(allowed_addresses=addresses_text, facilities_by_address=facilities_text)
    )

    conversation_after_chain = conversation_prompt | structured_llm_router

    return conversation_after_chain
