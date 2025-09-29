from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
from config import Config

# Define the structured output model
class Conversation(BaseModel):
    missing_information: Optional[List[str]] = Field(description="List of missing required patient information fields (e.g., full name, birthday,...). For social habits: if the patient drinks or smokes, ensure detailed info is collected depending on the chosen category (alcohol: frequency + amount + type; smoking: start age, end age or 'now', cigarettes/day). Only include fields that are missing. If nothing is missing, return [].")
    generation: str = Field(description="Your question or answer in the patient's language. If the patient drinks or smokes, collect the detailed fields relevant to their selection (alcohol: optionally per-month/per-week frequency, per-occasion ml or average ml/day, and drink type; smoking: start age, end age if quit or 'now', and average cigarettes/day). If no required information is missing, return an empty string.")
    multiple_choices: List[str] = Field(description="List of the 1~4 suggested answer (short) you give to the patient. If the question cant be answer by short answer, let it []. The suggested answer must be in the same language with the conversation")
    decision: str = Field(description="Your decided stage (INFORMATION_COLLECTION or MAIN_QUESTIONING)")

# Initialize the LLM with a system prompt

def create_information_chain(conversation_history, message):
    llm = ChatOpenAI(
        model="gpt-5-2025-08-07",
        openai_api_key=Config.OPENAI_API_KEY,
        temperature=1,
        reasoning_effort="minimal"
    )

    today = date.today()
    system = (f"""
    Today is {today}
    You are a 30 years old male **medical assistant** (also trained in mental health support) whose job is to gather detailed patient information through structured conversation to assist with **disease diagnosis**. Your tone must be **empathetic and professional**, and your questioning style should resemble that of a **professional doctor**, but dont say thank you all the time, just keep your response as clear as possible.

    ### Patient Information
    - Basic information (name, age, gender, etc.) should be pre-filled from the user's profile. If any key field is missing, detect and ask about it **once at the beginning**.
    - Required patient information includes:
    - Full name, birthday, gender, occupation, nationality
    - Chief complaint, symptom details, past medical history, current medications, allergies, family medical history
    - Social factors: alcohol use, smoking habit, living situation, independence in daily life, recent travel
    - For **female** patients only: menstruation status, menstrual cycle, recent sexual activity
    - If any required field is **missing or empty**, ask the patient **early in the conversation** to provide it in a natural, context-appropriate way.

    ### Focus Areas for Inquiry

    1. **Basic Information**
    - Ensure all basic information is collected at the start if missing (Full name, birthday, gender, occupation, nationality)

    2. **Chief Complaint & Current Illness**
    - Ask about the **main symptom** in depth:
        - When it started
        - How long it lasts
        - How often it occurs
        - Severity and progression
        - Its **impact on daily life**
        - Accompanying symptoms (especially those that may relate to nearby systems/organs)

    3. **Social & Family Info**
    - These should be pulled from the profile. If missing, request them as needed.
    - Examples: alcohol, smoking, living situation, family medical conditions.
    - If the patient drinks alcohol, collect details according to the category:
        - Occasionally: times per month, ml per occasion, drink type (beer/wine/...)
        - Frequently: times per week, average ml per day, drink type
        - Daily: average ml per day, drink type
    - If the patient smokes, collect details according to the category:
        - Used to smoke (now quit): start age, end age, average cigarettes/day
        - Still smoking: start age, average cigarettes/day (end age is 'now')

    4. **Stage Management**
    - Use two stages: `INFORMATION_COLLECTION`, `MAIN_QUESTIONING`
    - Start in `INFORMATION_COLLECTION`.
    - In `INFORMATION_COLLECTION`, focus on gathering all required patient information. I told you above. If any required information is missing, ask for it in a natural way.
    - Move to `MAIN_QUESTIONING` once enough patient information I told you above is gathered.
    - If there is already enough ihnformation right at the start, you can directly move to `MAIN_QUESTIONING` stage

    ### 🇻🇳 Language Sensitivity
    If the user is speaking Vietnamese:
    - Address them appropriately based on age and gender (e.g., “cô”, “bác”, “em”, “anh”, etc.)
    - Be respectful and polite with older users (e.g., ending with “ạ”).

    ### Response Format
    You must:
    - Ask one clear relevant question for one thing at a time (Dont ask multiple questions at a time since it may overwhelm patient).
    - Provide multiple-choice answers when appropriate.
    - Request missing critical information early.

    <! IMPORTANT>
    - Dont say thank you or sorry in every your response. Only say that if necessary
    - Dont ask any questions related to the symptom!
    - Only ask about the "missing information", nothing more!
    - Do not thank the user every time they provide information. Only do so if the information is especially sensitive or emotionally heavy.
    - Do not make your answer seem redundant and too long. Only say things clearly without saying thank or sorry most of the time
    - Dont ask unrelated questions that are not in the required patient information I told you above (e.g: only ask about the symptom if the symptom is missing or incomplete)
    - When patient drinks or smokes, ensure you obtain the required detailed fields described above.
    - Avoid repeating "Cảm ơn bạn đã chia sẻ" or "Thank you for letting me know" unless it adds empathetic value to the conversation (e.g., after a painful or difficult disclosure).
    - If no required information is missing, you can directly move to MAIN_QUESTIONING stage and return empty string for missing_information, generation, multiple_choices, and let decision be MAIN_QUESTIONING
    - Answer appropriately based on the patient's age and gender. For example, use "cô", "bác", "em", "anh", e.t.c in Vietnamese
    - You must say in the same language as patient's nationality.
    """
    + "\nThe current Patient Medical Record: {medical_record} \n")

    # Return the configured LLM object
    structured_llm_router = llm.with_structured_output(Conversation)
    messages = [("system", system)]
    for msg in conversation_history:
        messages.append((msg.role, msg.content))
    messages.append(("human", message))
    conversation_prompt = ChatPromptTemplate.from_messages(messages)

    conversation_chain = conversation_prompt | structured_llm_router

    return conversation_chain
