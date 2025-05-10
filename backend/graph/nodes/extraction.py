from graph.chains.extraction_chain import extraction_chain
from graph.state import GraphState
from typing import Any, Dict
from utils.displayer import Displayer
import threading

def extraction(state: GraphState) -> Dict[str, Any]:
    print("\n---EXTRACTION---")
    history = state["history"]

    displayer = Displayer()
    
    # Start progress bar in a separate thread
    progress_thread = threading.Thread(target=displayer.display_progress_bar, args=("Processing Medical Record...",))
    progress_thread.start()

    response = extraction_chain.invoke({"history": history})
    
    # Stop the progress bar
    progress_thread.join()

    # Display formatted output
    displayer.display_extraction_response(response)
    
    return {"medical_record": response, "previous_state": "EXTRACTION"}