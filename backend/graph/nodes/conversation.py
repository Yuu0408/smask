from entities.api_entities import GraphState
from typing import Any, Dict
from graph.chains.conversation_chain import conversation_chain
from rich import print
from rich.prompt import Prompt

def conversation(state: GraphState, user_message):
    print("\n---CONVERSATION---")

    if not user_message:
        print("[bold red]Waiting for user input...[/bold red]")
        return {"awaiting_input": True}

    history = state["history"] + f"\nPatient: {user_message}"
    medical_record = state["medical_record"]
    reasoning = state.get("reasoning", "")
    note = state.get("note", "")

    # Generate response
    response = conversation_chain.invoke({"history": history, "medical_record": medical_record, "reasoning": reasoning, "note": note})

    generation = response.generation
    decision = response.decision
    multiple_choices = response.multiple_choices
    reasoning = response.reasoning
    note = response.note
    # new_medical_record = response.medical_record

    history += f"\nYou: {generation}"
    print(f"[bold blue]Chat bot:[/bold blue] {generation}")

    state["decision"] = decision
    state["history"] = history
    state["reasoning"] = reasoning
    state["note"] = note
    # state["medical_record"] = new_medical_record

    return state, generation, multiple_choices