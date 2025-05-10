from graph.state import GraphState
from typing import Any, Dict
from graph.chains.follow_up_questions_chain import follow_up_questions_chain
from rich import print
from rich.prompt import Prompt


def follow_up(state: GraphState)-> Dict[str, Any]:
    previous_state = state["previous_state"]

    if previous_state != "not_follow_up":
        print("\n---FOLLOW UP QUESTION---")

    additional_info = state.get("additional_info", "")

    history = state["history"]

    if additional_info != "":
        user_input = Prompt.ask("[bold yellow]User[/bold yellow]")
        history += f"\nPatient: {user_input}"
        additional_info += f"\nPatient: {user_input}"
        previous_state = "FOLLOW UP QUESTION"
    else:
        previous_state = "not_follow_up"

    diagnosis = state["diagnosis_response"]
    questions = diagnosis.further_question_to_ask

    medical_record = state["medical_record"]

    # Generate response
    response = follow_up_questions_chain.invoke({"history": history, "questions": questions, "medical_record": medical_record})

    generation = response.generation
    # play_audio(generation)

    decision = response.decision
    
    # Update history with llm response
    history += f"\nYou: {generation}"
    additional_info += f"\nYou: {generation}"

    print(f"[bold blue]Chat bot:[/bold blue] {generation}")
    
    return {"decision": decision, "additional_info": history, "history": history, "previous_state": previous_state}
