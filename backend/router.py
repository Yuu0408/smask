from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from entities.api_entities import ConversationRequest, MedicalRecordRequest
from entities.patient_information_entity import PatientInformation
from graph.graph import app  # Your compiled LangGraph app
from graph.nodes.conversation_after import conversation_after
from graph.nodes.diagnosis import diagnosis
from graph.state import GraphState
from entities.medical_record_entity import MedicalRecord
from entities.predicted_diseases_entity import DiagnosisResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models.session_model import ChatSession
from uuid import UUID
from sqlalchemy.future import select
from graph.nodes.conversation import conversation
import json

api_router = APIRouter()

@api_router.post("/conversation", status_code=status.HTTP_201_CREATED)
async def process_conversation(
    request: ConversationRequest,
    db: AsyncSession = Depends(get_db)
):
    session_id = request.session_id
    user_message = request.user_message
    # Step 1: Fetch the session
    result = await db.execute(select(ChatSession).where(ChatSession.session_id == session_id))
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    def to_dict_if_pydantic(value):
        return value.dict() if hasattr(value, "dict") else value
    
    def to_json_dict(value):
        return json.loads(value.json()) if hasattr(value, "json") else value
    # Step 2: Deserialize state
    state: GraphState = {
        "todo": session_obj.todo,
        "diagnosis_paper": session_obj.diagnosis_paper,
        "note": session_obj.note,
        "reasoning": session_obj.reasoning,
        "history": session_obj.history,
        "decision": session_obj.decision,
        "medical_record": session_obj.medical_record,
        "diagnosis_response": session_obj.diagnosis_response,
        "additional_info": session_obj.additional_info,
        "follow_up_questions": session_obj.follow_up_questions,
        "previous_state": session_obj.previous_state
    }

    multiple_choices = []

    # Step 3: Use match-case on decision
    match state["decision"]:
        case "CONVERSATION":
            state, response, multiple_choices = conversation(state, user_message)

        case "DIAGNOSIS":
            state = diagnosis(state)
            state, response = conversation_after(state, user_message)
            multiple_choices = ["%medical_record%"]

        case "CONVERSATION_AFTER":
            state, response = conversation_after(state, user_message)
        case _:
            response = f"Unknown decision state: {state['decision']}"

    # Optionally update state or save response, etc.
    session_obj.todo = state["todo"]
    session_obj.diagnosis_paper = to_json_dict(state["diagnosis_paper"])
    session_obj.note = state["note"]
    session_obj.reasoning = state["reasoning"]
    session_obj.history = state["history"]
    session_obj.decision = state["decision"]
    session_obj.medical_record = to_json_dict(state["medical_record"])
    session_obj.diagnosis_response = to_json_dict(state["diagnosis_response"])
    session_obj.additional_info = state["additional_info"]
    session_obj.follow_up_questions = state["follow_up_questions"]
    session_obj.previous_state = state["previous_state"]

    await db.commit()
    
    return {"ai_response": response, "state": state, "multiple_choices": multiple_choices}

@api_router.post("/patient_info")
async def receive_patient_info(
    info: MedicalRecordRequest,
    db: AsyncSession = Depends(get_db)
):
    # Construct full MedicalRecord
    record = MedicalRecord(
        patient_info=MedicalRecord.PatientInformation(
            full_name=info.patient_info.full_name,
            birthday=info.patient_info.birthday,  # Extract year from birthday string
            gender=info.patient_info.gender,
            occupation=info.patient_info.occupation,
            nationality=info.patient_info.nationality,
            address=info.patient_info.address
        ),
        medical_history=MedicalRecord.MedicalHistory(
            chief_complaint=info.medical_history.chief_complaint,
            medical_history=info.medical_history.medical_history,
            past_medical_history=info.medical_history.past_medical_history,
            current_medications=info.medical_history.current_medications,
            allergies=info.medical_history.allergies,
            family_medical_history=info.medical_history.family_medical_history
        ),
        social_information=MedicalRecord.SocialInformation(**info.social_information.dict()),
        obstetric_gynecological_history=(
            MedicalRecord.ObstetricGynecologicalHistory(**info.obstetric_gynecological_history.dict())
            if info.obstetric_gynecological_history else None
        )
    )

    session = ChatSession(
        todo=None,
        diagnosis_paper={},
        note="",
        reasoning="",
        history="",
        decision="CONVERSATION",
        medical_record=json.loads(record.json()),
        diagnosis_response={},
        additional_info="",
        follow_up_questions=None,
        previous_state="CONVERSATION"
    )

    db.add(session)
    await db.commit()

    return {"message": "Patient info saved", "session_id": str(session.session_id)}