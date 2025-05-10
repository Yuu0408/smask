import joblib
from typing import Any, Dict
from graph.chains.re_diagnosis_chain import re_diagnosis_chain
from graph.state import GraphState
from utils.displayer import Displayer
import threading

def re_diagnosis(state: GraphState)-> Dict[str, Any]:
    print("\n---RE_DIAGNOSIS---")

    history = state["history"]

    medical_record = state["medical_record"]

    diagnosis_response = state["diagnosis_response"]

    additional_info = state["additional_info"]

    displayer = Displayer()
    
    # Start progress bar in a separate thread
    progress_thread = threading.Thread(target=displayer.display_progress_bar, args=("Processing Diagnosis...",))
    progress_thread.start()

    new_diagnosis = re_diagnosis_chain.invoke({"history": history, "medical_record": medical_record, "diagnosis": diagnosis_response, "additional_info": additional_info})

    # Stop the progress bar
    progress_thread.join()

    follow_up_questions = new_diagnosis.further_question_to_ask
    # wait_for_audio()
    # play_audio(generation)

    # Display formatted output
    displayer.display_diagnosis_response(new_diagnosis)
    
    return {"diagnosis_response": new_diagnosis, "follow_up_questions": follow_up_questions, "previous_state": "RE_DIAGNOSIS"}