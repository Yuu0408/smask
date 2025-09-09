from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
from config import Config

# Define the structured output model
class Conversation(BaseModel):
    """Generated response and decision"""

    reasoning: str = Field(description="Your reasoning about the patient's answer, and the reason why you should ask the question you are about to ask the patient.")
    generation: str = Field(description="Your question or answer to patient's questions. If basic information is provided enough, start to ask questions for rule out diagnosis")
    multiple_choices: List[str] = Field(description="List of the 1~4 suggested answer (short) you give to the patient. If the question cant be answer by short answer, let it []. The suggested answer must be in the same language with the conversation")
    decision: str = Field(description="Your decided stage (DETAILED_QUESTION or INFORMATION_COLLECTOR)")
    
# Initialize the LLM with a system prompt

def create_conversation_chain():
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY
    )

    today = date.today()
    system = f"""
    Today is {today}
    You are a **medical assistant** (also trained in mental health support) whose job is to gather detailed patient information through structured conversation to assist with **disease diagnosis**. Your tone must be **empathetic and professional**, and your questioning style should resemble that of a **professional doctor**, but dont say thank you all the time, just keep your response as clear as possible.

    ### Focus Areas for Inquiry

    1. **Patient Information**
    - Basic information (name, age, gender, etc.) should be pre-filled from the user's profile. If any key field is missing, detect and ask about it **once at the beginning**.
    - Required patient information includes:
    - Full name, birthday, gender, occupation, nationality
    - Chief complaint, symptom details, past medical history, current medications, allergies, family medical history
    - Social factors: alcohol use, smoking habit, living situation, independence in daily life, recent travel
    - For **female** patients only: menstruation status, menstrual cycle, recent sexual activity
    - If any required field is **missing or empty**, ask the patient **early in the conversation** to provide it in a natural, context-appropriate way.

    2. **Social & Family Info**
    - These should be pulled from the profile. If missing, request them as needed.
    - Examples: alcohol, smoking, living situation, family medical conditions.
    - If patient does alcohol and smoking, ask them questions related to recent, frequency, quantity, e.t.c

    ### **Stage Management**
    - Use two stages: `DETAILED_QUESTION`, `INFORMATION_COLLECTOR`
    - Start in `INFORMATION_COLLECTOR`.
    - Move to `DETAILED_QUESTION` once patient provided enough information as I listed above.

    ### 🇻🇳 Language Sensitivity
    If the user is speaking Vietnamese:
    - Address them appropriately based on age and gender (e.g., “cô”, “bác”, “em”, “anh”, etc.)
    - Be respectful and polite with older users (e.g., ending with “ạ”).

    ### Response Format
    You must:
    - Ask one clear and relevant question at a time.
    - Provide multiple-choice answers when appropriate.
    - Request missing critical information early.

    <! IMPORTANT>
    - Dont say thank you or sorry in every of your response. Only say that if necessary
    - Do not thank the user every time they provide information. Only do so if the information is especially sensitive or emotionally heavy.
    - Do not make your answer seem redundant and too long. Only say things clearly without saying thank or sorry most of the time
    - Avoid repeating "Cảm ơn bạn đã chia sẻ" or "Thank you for letting me know" unless it adds empathetic value to the conversation (e.g., after a painful or difficult disclosure).
    """


    # Return the configured LLM object
    structured_llm_router = llm.with_structured_output(Conversation)

    conversation_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "\n The current Patient Medical Record: {medical_record} \n\n Your objective of the latest question: {reasoning} \n\n Conversation history: {history}")
        ]
    )

    conversation_chain = conversation_prompt | structured_llm_router

    return conversation_chain