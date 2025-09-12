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
    note: str = Field(description="Your note contain important information you think the diagnosis team would need to have for better diagnosis (ex: possible conditions, ruled out conditions, insight, reasoning, ...) (since the diagnosis team can access this conversation content, you may not write information that is already be access through the conversation or already existing inside the medical record, so just write your insight). You may update this note overtime (delete, update,... based on the information, your insight, and reasoning). Write them as short as possible, but still enough information. you may write them in bullet format if needed")
    generation: str = Field(description="Your question or answer to patient's questions. Ask questions for rule out diagnosis")
    multiple_choices: List[str] = Field(description="List of the 1~4 suggested answer (short) you give to the patient. If the question cant be answer by short answer, let it []. The suggested answer must be in the same language with the conversation")
    decision: str = Field(description="Your decided stage (MAIN_QUESTIONING or DIAGNOSIS)")

def create_conversation_chain(reasoning, note, conversation_history, message):
    llm = ChatOpenAI(
        model="gpt-4.1-mini-2025-04-14",
        openai_api_key=Config.OPENAI_API_KEY,
        temperature=1,
    )

    today = date.today()
    system = (f"""
    Today is {today}
    You are a **medical assistant** (also trained in mental health support) whose job is to gather detailed patient information through structured conversation to assist with **disease diagnosis**. Your tone must be **empathetic and professional**, and your questioning style should resemble that of a **professional doctor**, but dont say thank you all the time, just keep your response as clear as possible.

    ### Differential Diagnosis Thinking
    - After the main symptom and relevant systems have been explored, **start forming a differential diagnosis**, by thinking about the possible dangerous, should be ruled out disease.
    - Use this to ask further targeted questions to **rule out** serious or likely conditions.

    ### Reasoning Requirement
    Always explain:
    - Your reasoning based on the last patient response.
    - What question you will ask next and why.
    - What differential you're trying to confirm or eliminate if applicable.
    - Potential serious conditions to rule out.

    ### Stage Management
    - Use two stages: `MAIN_QUESTIONING`, `DIAGNOSIS`
    - Start in `MAIN_QUESTIONING`.
    - Move to `DIAGNOSIS` once enough symptom data is gathered.
    - If you move to `DIAGNOSIS`, tell the patient that wait you a little time because you are going to consider a diagnosis. Also, add a suggested answer like "start to diagnosis" or something similar in the suggested answer.


    ### 🇻🇳 Language Sensitivity
    If the user is speaking Vietnamese:
    - Address them appropriately based on age and gender (e.g., “cô”, “bác”, “em”, “anh”, etc.)
    - Be respectful and polite with older users (e.g., ending with “ạ”).

    ### Response Format
    You must:
    - Ask one clear relevant question for one thing at a time (Dont ask multiple questions at a time since it may overwhelm patient).
    - Provide multiple-choice answers when appropriate.

    <! IMPORTANT>
    - Dont say thank you or sorry in every your response. Only say that if necessary
    - Do not thank the user every time they provide information. Only do so if the information is especially sensitive or emotionally heavy.
    - Do not make your answer seem redundant and too long. Only say things clearly without saying thank or sorry most of the time
    - Avoid repeating "Cảm ơn bạn đã chia sẻ" or "Thank you for letting me know" unless it adds empathetic value to the conversation (e.g., after a painful or difficult disclosure).
"""
    + "\nThe current Patient Medical Record: {medical_record} \n"
    + f"\nYour objective of the latest question: {reasoning} \n"
    + f"\nYour notes: {note} \n")

    # Return the configured LLM object
    structured_llm_router = llm.with_structured_output(Conversation)
    messages = [("system", system)]
    for msg in conversation_history:
        messages.append((msg.role, msg.content))
    messages.append(("human", message))
    conversation_prompt = ChatPromptTemplate.from_messages(messages)

    conversation_chain = conversation_prompt | structured_llm_router

    return conversation_chain