from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from entities.medical_record_entity import MedicalRecord
from config import Config

# Initialize the LLM with a system prompt
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=Config.OPENAI_API_KEY
)

system ="""
    You are a professional Medical Information Extractor. Your task is to analyze the additional conversations between a medical assistant and a patient and accurately complete the structured medical record form. Ensure completeness, resolve ambiguities, and correctly map information to the appropriate fields while maintaining the intended meaning of the patient's responses.
"""

# Return the configured LLM object
structured_llm_router = llm.with_structured_output(MedicalRecord)

extraction_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "###Additional Conversation: \n{additional_info}\n\n###Current Medical Record: {medical_record}")
    ]
)

process_additional_info_chain = extraction_prompt | structured_llm_router