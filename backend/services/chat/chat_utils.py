from graph.chains.conversation_chain import create_conversation_chain

def get_ai_response(medical_record, reasoning, history, message):
    conversation_chain = create_conversation_chain(reasoning=reasoning, conversation_history=history, message=message)
    response = conversation_chain.invoke({"medical_record": medical_record})

    return response