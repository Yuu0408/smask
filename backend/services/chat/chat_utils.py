from datetime import date, datetime
from typing import Any, Dict, Optional

from graph.chains.basic_questions_chain import create_basic_questions_chain
from graph.chains.closing_chain import create_closing_chain
from graph.chains.diagnostic_reasoning_chain import create_diagnostic_reasoning_chain
from graph.chains.form_clarification_chain import create_form_clarification_chain
from graph.chains.record_update_chain import create_record_update_chain
from graph.chains.final_diagnosis_chain import create_final_diagnosis_chain
from graph.chains.rule_out_selection_chain import create_rule_out_selection_chain
from graph.chains.rule_out_in_chain import create_rule_out_in_chain
from graph.chains.state_update_chain import create_state_update_chain
from graph.chains.next_step_chain import create_next_step_chain
from services.contact.options import get_allowed_addresses, get_facilities_by_address


def _compute_age(birthday_value: Any) -> Optional[int]:
    """Convert a birthday into an integer age in years, if possible."""
    dob: Optional[date] = None
    if isinstance(birthday_value, datetime):
        dob = birthday_value.date()
    elif isinstance(birthday_value, date):
        dob = birthday_value
    elif isinstance(birthday_value, str):
        try:
            dob = date.fromisoformat(birthday_value[:10])
        except Exception:
            dob = None

    if not dob:
        return None

    today = date.today()
    age = today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )
    return age if age >= 0 else None


def _extract_patient_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build a compact patient profile (age/gender/name) for tone control."""
    profile: Dict[str, Any] = {}
    basic_info = (state.get("basic_form") or {}).get("patient_info") or {}
    clarified_info = (state.get("clarified_form") or {}).get("patient_info") or {}
    merged_info = {**basic_info, **clarified_info}

    gender = merged_info.get("gender")
    if gender:
        profile["gender"] = gender

    birthday = merged_info.get("birthday")
    age = _compute_age(birthday)
    if age is not None:
        profile["age"] = age

    def _derive_vn_address_term(age_val: Optional[int], gender_val: Optional[str]) -> Optional[str]:
        gender_norm = (gender_val or "").lower()
        if age_val is not None:
            if age_val >= 60:
                return "bác"
            if age_val >= 40:
                if gender_norm == "male":
                    return "anh"
                if gender_norm == "female":
                    return "chị"
                return "bạn"
            if age_val >= 25:
                if gender_norm == "male":
                    return "anh"
                if gender_norm == "female":
                    return "chị"
                return "bạn"
            # Younger than assistant's persona; use "em" politely
            return "em"
        return None

    address_term_vi = _derive_vn_address_term(age, gender)
    if address_term_vi:
        profile["address_term_vi"] = address_term_vi
        profile["possessive_vi"] = f"của {address_term_vi}"

    return profile


def _normalize_state(shared_state) -> Dict[str, Any]:
    if hasattr(shared_state, "model_dump"):
        state: Dict[str, Any] = shared_state.model_dump(mode="json")
    else:
        state = shared_state or {}

    state = dict(state or {})

    # Redact full_name to avoid repeating it in patient-facing prompts
    for key in ("basic_form", "clarified_form"):
        section = state.get(key)
        if isinstance(section, dict):
            section_copy = dict(section)
            patient_info = section_copy.get("patient_info")
            if isinstance(patient_info, dict) and "full_name" in patient_info:
                pi_copy = dict(patient_info)
                pi_copy.pop("full_name", None)
                section_copy["patient_info"] = pi_copy
            state[key] = section_copy

    profile = _extract_patient_profile(state)
    if profile:
        state["patient_profile"] = profile
    return state


def _condense_rule_out_state(shared_state) -> Dict[str, Any]:
    """Compact snapshot for question selection to avoid full conversation bloat."""
    state = _normalize_state(shared_state)
    condensed: Dict[str, Any] = {
        "reasoning_snapshot": state.get("reasoning_snapshot"),
        "symptom_notes": state.get("symptom_notes", []),
        "asked_targets": state.get("asked_targets", []),
        "pending_questions": state.get("pending_questions", []),
        "info_gaps_symptom": state.get("info_gaps_symptom", []),
        "red_flags": state.get("red_flags", []),
        "last_question": state.get("last_question"),
        "patient_profile": state.get("patient_profile"),
        "selection_plan": state.get("selection_plan"),
    }

    # Append short conversation tail for intent/answer detection without full history
    condensed["conversation_tail"] = (state.get("conversation_tail") or [])[-8:]

    return condensed


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


def run_rule_out_question(shared_state, selection_plan=None):
    chain = create_rule_out_in_chain()
    return chain.invoke(
        {
            # Use full state (includes conversation) for final wording and tone
            "state": _normalize_state(shared_state),
            "selection_plan": selection_plan or {},
        }
    )


def run_rule_out_selection(shared_state):
    chain = create_rule_out_selection_chain()
    return chain.invoke(
        {
            # Use condensed state to pick target without full conversation
            "state": _condense_rule_out_state(shared_state),
        }
    )


def run_record_update(shared_state):
    chain = create_record_update_chain()
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


def _format_conversation_history(conversation: Any, *, limit: int = 30) -> str:
    """Format a conversation list into readable lines for prompts."""
    items = list(conversation or [])
    if limit and limit > 0:
        items = items[-limit:]

    lines = []
    for entry in items:
        role = ""
        content = ""
        if isinstance(entry, dict):
            role = entry.get("role") or ""
            content = entry.get("content") or ""
        else:
            role = getattr(entry, "role", "") or ""
            content = getattr(entry, "content", "") or ""
        role_text = role.upper() if role else "UNKNOWN"
        lines.append(f"{role_text}: {content}")
    return "\n".join(lines) if lines else "(no conversation yet)"


def run_next_step(shared_state):
    chain = create_next_step_chain(
        allowed_addresses=get_allowed_addresses(),
        facilities_by_address=get_facilities_by_address(),
    )
    state_json = _normalize_state(shared_state)
    history_text = _format_conversation_history(state_json.get("conversation_tail"))
    return chain.invoke({"conversation_history": history_text})


def run_final_diagnosis(shared_state):
    chain = create_final_diagnosis_chain()
    return chain.invoke(
        {
            "state": _normalize_state(shared_state),
        }
    )
