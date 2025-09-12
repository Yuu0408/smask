from graph.chains.conversation_chain import create_conversation_chain
from graph.chains.information_chain import create_information_chain

def get_ai_response(medical_record, reasoning, note, history, message):
    conversation_chain = create_conversation_chain(reasoning=reasoning, note=note, conversation_history=history, message=message)
    response = conversation_chain.invoke({"medical_record": medical_record})

    return response

def get_information(medical_record, history, message):
    information_chain = create_information_chain(conversation_history=history, message=message)
    response = information_chain.invoke({"medical_record": medical_record})

    return response