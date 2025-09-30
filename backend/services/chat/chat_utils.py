from graph.chains.extraction_chain import create_extraction_chain
from graph.chains.conversation_after_chain import create_conversation_after_chain
from graph.chains.conversation_chain import create_conversation_chain
from graph.chains.information_chain import create_information_chain
from graph.chains.diagnosis_chain import create_diagnosis_chain
from services.contact.options import get_allowed_addresses, get_facilities_by_address
import json

def _normalize_record(medical_record):
    try:
        if hasattr(medical_record, 'data'):
            return getattr(medical_record, 'data') or {}
    except Exception:
        pass
    return medical_record or {}

def get_ai_response(medical_record, reasoning, note, history, message, diseases_already_asked, disease_to_ask):
    # Ensure plain-text for prompt interpolation
    if isinstance(reasoning, (dict, list)):
        try:
            reasoning_text = json.dumps(reasoning, ensure_ascii=False)
        except Exception:
            reasoning_text = str(reasoning)
    elif reasoning is None:
        reasoning_text = ""
    else:
        reasoning_text = str(reasoning)

    note_text = "" if note is None else str(note)

    conversation_chain = create_conversation_chain(
        reasoning=reasoning_text,
        note=note_text,
        conversation_history=history,
        message=message,
        diseases_already_asked=diseases_already_asked,
        disease_to_ask=disease_to_ask
    )
    response = conversation_chain.invoke({"medical_record": _normalize_record(medical_record), "reasoning": reasoning, "note": note_text, "diseases_already_asked": diseases_already_asked})

    return response

def get_information(medical_record, history, message):
    information_chain = create_information_chain(conversation_history=history, message=message)
    response = information_chain.invoke({"medical_record": _normalize_record(medical_record)})

    return response

def get_diagnosis(medical_record, history, note):
    diagnosis_chain = create_diagnosis_chain()
    response = diagnosis_chain.invoke({"medical_record": _normalize_record(medical_record), "history": history, "note": note})

    return response

def get_conversation_after(diagnosis, history, message, medical_record):
    if message == "###DIAGNOSIS###":
        dummy_message = ""
    else:
        dummy_message = message
    allowed_addresses = get_allowed_addresses()
    facilities_by_address = get_facilities_by_address()
    conversation_after_chain = create_conversation_after_chain(conversation_history=history, message=dummy_message, allowed_addresses=allowed_addresses, facilities_by_address=facilities_by_address)
    response = conversation_after_chain.invoke({"diagnosis": diagnosis, "medical_record": _normalize_record(medical_record)})

    return response

def update_medical_record(medical_record, history):
    update_medical_record_chain = create_extraction_chain()
    response = update_medical_record_chain.invoke({"medical_record": _normalize_record(medical_record), "history": history})

    return response


