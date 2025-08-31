from graph.chains.conversation_chain import create_conversation_chain

def get_ai_response(history, medical_record, reasoning, note):
    conversation_chain = create_conversation_chain()
    response = conversation_chain.invoke({"history": history, "medical_record": medical_record, "reasoning": reasoning, "note": note})

    return response