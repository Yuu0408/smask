from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import END, StateGraph

from graph.consts import CONVERSATION, EXTRACTION, DIAGNOSIS, CONVERSATION_AFTER, PROCESS_ADDITIONAL_INFO, RE_DIAGNOSIS, FOLLOW_UP

from graph.nodes.conversation import conversation
from graph.nodes.extraction import extraction
from graph.nodes.diagnosis import diagnosis
from graph.nodes.conversation_after import conversation_after
from graph.nodes.follow_up_questions import follow_up
from graph.nodes.process_additional_info import process_additional_info
from graph.nodes.re_diagnosis import re_diagnosis

from graph.state import GraphState

def decide_to_extraction(state: GraphState) -> str:
    print("\n---CONSIDERING CONVERSATION OR EXTRACTION---")

    if state["decision"] == "CONVERSATION":
        print(
            "---DECISION: REMAIN CONVERSATION---"
        )
        return CONVERSATION
    else:
        print("---DECISION: GO TO EXTRACTION---")
        return EXTRACTION

def decide_to_process(state: GraphState) -> str:
    if state["previous_state"] != "FOLLOW UP QUESTION":
        return FOLLOW_UP
    
    print("\n---CONSIDERING FOLLOW UP QUESTION OR PROCESS ADDITIONAL INFO---")

    if state["decision"] == "CONVERSATION":
        print(
            "---DECISION: REMAIN FOLLOW UP QUESTION---"
        )
        return FOLLOW_UP
    else:
        print("---DECISION: GO TO PROCESS ADDITIONAL INFO---")
        return PROCESS_ADDITIONAL_INFO

def decide_to_diagnosis_or_conversation(state: GraphState) -> str:
    print("\n---CONSIDERING DIAGNOSIS OR CONVERSATION---")

    if state["decision"] == "CONVERSATION":
        print(
            "---DECISION: GO TO CONVERSATION---"
        )
        return CONVERSATION_AFTER
    else:
        print("---DECISION: GO TO DIAGNOSIS---")
        return DIAGNOSIS
    
def decide_to_extraction_after(state: GraphState) -> str:
    if state["previous_state"] != "CONVERSATION_AFTER":
        return CONVERSATION_AFTER
    
    print("\n---CONSIDERING CONVERSATION OR RE_DIAGNOSIS OR END---")

    if state["decision"] == "CONVERSATION":
        print(
            "---DECISION: REMAIN CONVERSATION---"
        )
        return CONVERSATION_AFTER
    elif state["decision"] == "DIAGNOSIS":
        print("---DECISION: GO TO RE_DIAGNOSIS---")
        return PROCESS_ADDITIONAL_INFO
    else:
        print("---DECISION: END CONVERSATION---")
        return END

def decide_to_conversation_or_follow_up_question(state: GraphState) -> str:
    print("\n---CONSIDERING FOLLOW UP QUESTIONS OR FINAL CONVERSATION")

    follow_up_question = state["follow_up_questions"]
    if follow_up_question is None or follow_up_question == []:
        print("---DECISION: GO TO FINAL CONVERSATION---")
        return CONVERSATION_AFTER
    else:
        print("---DECISION: GO TO ASKING FOLLOW UP QUESTIONS")
        return FOLLOW_UP


workflow = StateGraph(GraphState)
workflow.add_node(CONVERSATION, conversation)
workflow.add_node(EXTRACTION, extraction)
workflow.add_node(DIAGNOSIS, diagnosis)
workflow.add_node(FOLLOW_UP, follow_up)
workflow.add_node(PROCESS_ADDITIONAL_INFO, process_additional_info)
workflow.add_node(RE_DIAGNOSIS, re_diagnosis)
workflow.add_node(CONVERSATION_AFTER, conversation_after)

workflow.set_entry_point(CONVERSATION)

workflow.add_conditional_edges(
    CONVERSATION,
    decide_to_extraction,
    path_map={
        CONVERSATION: CONVERSATION,
        EXTRACTION: EXTRACTION,
    },
)

workflow.add_edge(EXTRACTION, DIAGNOSIS)

workflow.add_conditional_edges(
    DIAGNOSIS,
    decide_to_conversation_or_follow_up_question,
    path_map={
        CONVERSATION_AFTER: CONVERSATION_AFTER,
        FOLLOW_UP: FOLLOW_UP
    },
)

workflow.add_conditional_edges(
    FOLLOW_UP,
    decide_to_process,
    path_map={
        FOLLOW_UP: FOLLOW_UP,
        PROCESS_ADDITIONAL_INFO: PROCESS_ADDITIONAL_INFO,
    },
)

workflow.add_edge(PROCESS_ADDITIONAL_INFO, RE_DIAGNOSIS)

workflow.add_conditional_edges(
    RE_DIAGNOSIS,
    decide_to_conversation_or_follow_up_question,
    path_map={
        CONVERSATION_AFTER: CONVERSATION_AFTER,
        FOLLOW_UP: FOLLOW_UP
    },
)

workflow.add_conditional_edges(
    CONVERSATION_AFTER,
    decide_to_extraction_after,
    path_map={
        CONVERSATION_AFTER: CONVERSATION_AFTER,
        PROCESS_ADDITIONAL_INFO: PROCESS_ADDITIONAL_INFO,
        END: END,
    },
)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")