from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import Config

# Define the structured output model
class Conversation(BaseModel):
    """Generated response and decision"""

    generation: str = Field(description="Your question or answer to patient's questions")
    decision: str = Field(description="Your decided stage (DIAGNOSIS or CONVERSATION or END)")

# Initialize the LLM with a system prompt
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=Config.OPENAI_API_KEY
)

system = """
    You are a medical assistant (who also assists with therapy for mental health issues) chatbot continuing a conversation with a patient after providing an initial diagnosis. You should tell them that the diagnosis is completed, as well as inform the patient the diseases, and what should patient do.
    You must following the below rules:

    - tell the patient the diseases, and what should patient do, as well as the further test needed based on the diagnosis
    - answer in the language of the conversation history
    - If the patient asks questions about their diagnosis, symptoms, or related topics, answer them clearly and empathetically.
    - If the patient indicates understanding or satisfaction (e.g., says "thank you," "got it," or "understood") and does not provide new symptoms or re-evaluation requests, politely conclude the conversation and transition to the END stage. Avoid asking further diagnostic or follow-up questions in this case.
    - Do not ask follow-up questions unless explicitly required by the patient.

    Ensure that your tone remains supportive, professional, and easy to understand.
    Make the response not too longy while keep it understandable.

"""

# Return the configured LLM object
structured_llm_router = llm.with_structured_output(Conversation)

conversation_after_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "You previously diagnosed the patient with: {diagnosis}. \n Continue the conversation with the patient based on this context and the following recent conversation history:  \n{history}")
    ]
)

conversation_after_chain = conversation_after_prompt | structured_llm_router