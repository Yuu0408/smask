import joblib
from typing import Any, Dict
from entities.predicted_diseases_entity import DiagnosisPaper
from graph.chains.diagnosis_chain import diagnosis_chain
from graph.state import GraphState
from utils.displayer import Displayer
import threading

def diagnosis(state: GraphState):
    print("\n---DIAGNOSIS---")

    medical_record = state["medical_record"]
    history = state["history"]
    note = state["note"]

    displayer = Displayer()
    
    # Start progress bar in a separate thread
    progress_thread = threading.Thread(target=displayer.display_progress_bar, args=("Processing Diagnosis...",))
    progress_thread.start()
    
    diagnosis_response = diagnosis_chain.invoke({"history": history, "medical_record": medical_record, "note": note})
    # follow_up_questions = diagnosis_response.further_question_to_ask
    # generation = diagnosis_response.generation
    previous_state = "DIAGNOSIS"
    
    # Stop the progress bar
    progress_thread.join()
    
    # Display formatted output
    displayer.display_diagnosis_response(diagnosis_response)
    diagnosis_paper = DiagnosisPaper(
        reasoning_process=diagnosis_response.reasoning_process,
        diagnosis=diagnosis_response.diagnosis,
        further_test=diagnosis_response.further_test
    )


    # state["follow_up_questions"] = follow_up_questions
    state["previous_state"] = previous_state
    state["decision"] = "CONVERSATION_AFTER"
    state["medical_record"] = diagnosis_response.medical_record
    state["diagnosis_paper"] = diagnosis_paper
    state["todo"] = diagnosis_response.todo
    
    # wait_for_audio()
    # play_audio(generation)
    
    return state