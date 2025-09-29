from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
from config import Config

# Define the structured output model
class Conversation(BaseModel):
    """Generated response and decision"""
    class Reasoning(BaseModel):
        class PredictedDisease(BaseModel):
            name: str = Field(..., description="The name of the diagnosed or predicted disease.")
            symptoms: List[str] = Field(..., description="List of symptoms associated with the disease.")
            supporting_evidence: List[str] = Field(..., description="List of symptoms you can tell from patient that supports the diagnosis.")
            differentiating_factor: Optional[str] = Field(None, description="Key factor that differentiates this disease from others.")

        most_likely: Optional[PredictedDisease] = Field(
            None, description="The condition most strongly supported by the patient's symptoms and history."
        )
        
        possible_diagnoses: List[PredictedDisease] = Field(
            default_factory=list, description="Other plausible diagnoses that may explain the patient's symptoms."
        )
        
        rule_out: List[PredictedDisease] = Field(
            default_factory=list, description="Dangerous or serious conditions that might not fully match the case but must be ruled out carefully due to risk."
        )

        diseases_to_ask: List[str] = Field(
            default_factory=list, description="List of all diseases still need to ask about (including most likely, possible, and rule out diseases).")

        already_asked_diseases: List[str] = Field(default_factory=list, description="List of diseases you already asked about") 
        current_disease_to_ask: Optional[str] = Field(None, description="The disease you are currently asking about. Must be one of the diseases in diseases_to_ask")

    reasoning: Reasoning = Field(default_factory=Reasoning, description="Your reasoning based on the last patient response. What question you will ask next and why. What differential you're trying to confirm or eliminate if applicable. Potential serious conditions to rule out")
    note: str = Field(default="", description="Your note contain important information you think the diagnosis team would need to have for better diagnosis (ex: possible conditions, ruled out conditions, insight, reasoning, ...) (since the diagnosis team can access this conversation content, you may not write information that is already be access through the conversation or already existing inside the medical record, so just write your insight). You may update this note overtime (delete, update,... based on the information, your insight, and reasoning). Write them as short as possible, but still enough information. you may write them in bullet format if needed")
    generation: str = Field(default="", description="Your question or answer to patient's questions. Ask questions for rule out potential diseases, from the following order: 1, need to be ruled out dangerous diseases 2, Most potential disease 3, Other possible diseases. You must ask one clear relevant question for one thing at a time (Dont ask multiple questions at a time since it may overwhelm patient). For example, instead of asking question like do you have headache or sweat, which are two things: headache and sweat, you must ask headache on one question, then asking sweat on another question. Provide multiple-choice answers when appropriate.")
    multiple_choices: List[str] = Field(default_factory=list, description="List of the 1~4 suggested answer (short) you give to the patient. If the question cant be answer by short answer, let it []. The suggested answer must be in the same language with the conversation")
    decision: str = Field(default="MAIN_QUESTIONING", description="Your decided stage (MAIN_QUESTIONING or DIAGNOSIS)")

def create_conversation_chain(reasoning, note, conversation_history, message):
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=Config.OPENAI_API_KEY,
        temperature=1,
    )

    today = date.today()
    system = (f"""
    Today is {today}
    You are a 30 years old **medical assistant** (also trained in mental health support) whose job is to gather detailed patient information through structured conversation to assist with **disease diagnosis**. Your tone must be **empathetic and professional**, and your questioning style should resemble that of a **professional doctor**, but dont say thank you all the time, just keep your response as clear as possible.

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
    - Move to `DIAGNOSIS` once enough symptom data is gathered, and you have a clear differential diagnosis to present.
    - If you move to `DIAGNOSIS`, tell the patient that wait you a little time because you are going to consider a diagnosis.


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
    - For reasoning, you can update it based on the new information from patient, like adding new potential conditions, removing ruled out conditions, updating your insight and reasoning. But keep it as short as possible.

    <!!! ESPECIALLY IMPORTANT>
    - Always ask only one symptom per question.  
    Do not combine multiple conditions in a single sentence.  
    Example: Ask “Do you have a headache?” → after the answer, ask “Do you feel tired?”
    - Never move to DIAGNOSIS stage unless you have asked all questions to rule out all the diseases (ensure you asked all the symptoms related to: rule out dangerous diseases, most likely disease, other possible diseases). Only move to DIAGNOSIS stage when you have asked enough questions to cover all the symptoms related to the potential conditions you have in your reasoning.
    """
    + "\nThe current Patient Medical Record: {medical_record} \n"
    + "\nYour objective of the latest question: {reasoning} \n"
    + f"\nYour notes: {note} \n"
    + "\nOutput schema requirements: reasoning, note, generation, multiple_choices, decision. Decision must be exactly one of MAIN_QUESTIONING or DIAGNOSIS.\n"
    )

    # Return the configured LLM object
    structured_llm_router = llm.with_structured_output(Conversation)
    messages = [("system", system)]
    for msg in conversation_history:
        messages.append((msg.role, msg.content))
    messages.append(("human", message))
    conversation_prompt = ChatPromptTemplate.from_messages(messages)

    conversation_chain = conversation_prompt | structured_llm_router

    return conversation_chain
