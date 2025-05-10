from graph.state import GraphState
from typing import Any, Dict
from graph.chains.conversation_after_chain import conversation_after_chain
from rich import print
from rich.prompt import Prompt


def conversation_after(state: GraphState, user_message):
    # previous_state = state["previous_state"]

    # if previous_state != "not_conversation":
    #     print("\n---CONVERSATION_AFTER---")

    # history = state["history"]
    # additional_info = state.get("additional_info", "")

    # if previous_state == "not_conversation":
    #     user_input = Prompt.ask("[bold yellow]User[/bold yellow]")
    #     history += f"\nPatient: {user_input}"
    #     additional_info += f"\nPatient: {user_input}"
    #     previous_state = "CONVERSATION_AFTER"
    # else:
    #     previous_state = "not_conversation"

    # diagnosis = state["diagnosis_response"]
    # Generate response

    diagnosis_paper = state["diagnosis_paper"]
    history = state["history"]
    history = state["history"] + f"\nPatient: {user_message}"
    response = conversation_after_chain.invoke({"diagnosis": diagnosis_paper, "history": history})

    generation = response.generation
    # play_audio(generation)

    decision = response.decision
    
    # Update history with llm response
    history += f"\nYou: {generation}"
    # additional_info += f"\nYou: {generation}"

    state["history"] = history

    print(f"[bold blue]Chat bot:[/bold blue] {generation}")
    
    return state, generation
