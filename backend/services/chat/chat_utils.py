from typing import Any, Dict

from graph.chains.basic_questions_chain import create_basic_questions_chain
from graph.chains.closing_chain import create_closing_chain
from graph.chains.diagnostic_reasoning_chain import create_diagnostic_reasoning_chain
from graph.chains.form_clarification_chain import create_form_clarification_chain
from graph.chains.rule_out_in_chain import create_rule_out_in_chain
from graph.chains.state_update_chain import create_state_update_chain
from services.contact.options import get_allowed_addresses, get_facilities_by_address


def _normalize_state(shared_state) -> Dict[str, Any]:
    if hasattr(shared_state, "model_dump"):
        return shared_state.model_dump(mode="json")
    return shared_state or {}


def run_state_update(shared_state, last_question, patient_message):
    chain = create_state_update_chain()
    return chain.invoke(
        {
            "state": _normalize_state(shared_state),
            "last_question": last_question,
            "patient_message": patient_message,
        }
    )


def run_form_clarification(shared_state, latest_message: str = ""):
    chain = create_form_clarification_chain()
    return chain.invoke({"state": _normalize_state(shared_state), "latest_message": latest_message})


def run_basic_question(shared_state):
    chain = create_basic_questions_chain()
    return chain.invoke(
        {
            "state": _normalize_state(shared_state),
        }
    )


def run_diagnostic_reasoning(shared_state):
    chain = create_diagnostic_reasoning_chain()
    state_json = _normalize_state(shared_state)
    return chain.invoke(
        {
            "state": state_json,
        }
    )


def run_rule_out_question(shared_state):
    chain = create_rule_out_in_chain()
    return chain.invoke(
        {
            "state": _normalize_state(shared_state),
        }
    )


def run_closing(shared_state):
    chain = create_closing_chain(
        allowed_addresses=get_allowed_addresses(),
        facilities_by_address=get_facilities_by_address(),
    )
    state_json = _normalize_state(shared_state)
    return chain.invoke(
        {
            "state": state_json,
            "reasoning_snapshot": state_json.get("reasoning_snapshot"),
        }
    )
