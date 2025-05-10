from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import Config

# Define the structured output model
class Conversation(BaseModel):
    """Generated response and decision"""

    generation: str = Field(description="Your question or answer to patient's questions")
    decision: str = Field(description="Your decided stage (DIAGNOSIS or CONVERSATION")

# Initialize the LLM with a system prompt
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=Config.OPENAI_API_KEY
)

system = """
    # Task:
    You are a medical assistant (who also assists with therapy for mental health issues) chatbot continuing a conversation with a patient after providing an initial diagnosis, to confirm / gain more information, to conduct the diagnosis again.
    You must following the below rules:
    - Dont ask too many questions at the same times
    - Only ask one question at a time
    - Ensure that your tone remains supportive, professional, and easy to understand.
    - Make the response not too longy while keep it understandable.
    - If the gathered symptoms are **sufficient for diagnosis**, **transition to the EXTRACTION stage** and inform the patient that you will analyze their condition.  
    - If **more information is needed**, **stay in the CONVERSATION stage** and continue asking relevant questions.  

"""

# Return the configured LLM object
structured_llm_router = llm.with_structured_output(Conversation)

conversation_after_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("system", "###Questions need to ask: {questions}"),
        ("human", "###Medical record: {medical_record}.\n\n###Chat history: {history}.")
    ]
)

follow_up_questions_chain = conversation_after_prompt | structured_llm_router