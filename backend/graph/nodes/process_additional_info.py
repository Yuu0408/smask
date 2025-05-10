from graph.chains.process_additional_info_chain import process_additional_info_chain
from graph.state import GraphState
from typing import Any, Dict
from utils.displayer import Displayer
import threading

def process_additional_info(state: GraphState)-> Dict[str, Any]:
    print("\n---PROCESS ADDITIONAL INFO---")

    additional_info = state["additional_info"]

    medical_record = state["medical_record"]

    displayer = Displayer()
    
    # Start progress bar in a separate thread
    progress_thread = threading.Thread(target=displayer.display_progress_bar, args=("Processing Medical Record...",))
    progress_thread.start()

    response = process_additional_info_chain.invoke({"additional_info": additional_info, "medical_record": medical_record})

    # Stop the progress bar
    progress_thread.join()

    # Display formatted output
    displayer.display_extraction_response(response)
    
    return {"medical_record": response, "additional_info": "", "previous_state": "PROCESS ADDITIONAL INFO"}


