from services.chat.chat_utils import get_ai_response, get_information
from sqlmodel import Session
from fastapi import HTTPException
from repositories import MedicalRecordRepo, ChatHistoryRepo, AIStateRepo
import uuid
from models.dto.modelDto import AIStateData, AddMedicalRecordRequest, AddMedicalRecordResponse, ChatMessageDto, ChatTextRequest, ChatTextResponse, GetAllChatHistoryRequest, GetChatHistoryRequest, GetChatHistoryResponse, GetCurrentRecordRequest, GetCurrentRecordResponse

class HistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repo = MedicalRecordRepo(db)
        self.chat_history_repo = ChatHistoryRepo(db)
        self.ai_state_repo = AIStateRepo(db)

    async def get_all_history(self, request: GetAllChatHistoryRequest):
        user_id = request.user_id

        if not user_id:
            raise HTTPException(status_code=400, detail=f'Invalid user id')
        
        rows = self.chat_history_repo.get_all_chat_history(
            user_id=request.user_id,
        )
        # Build a preview per conversation (record_id): last message (100 chars) and last activity time
        previews_by_record: dict[str, dict] = {}
        record_ids: set[str] = set()
        for row in rows:
            key = str(row.record_id)
            # Since rows are ordered asc by created_at, simply overwrite to keep the last message
            previews_by_record[key] = {
                "sessionId": key,
                # earliest created_at isn't required for preview; expose last activity time for sorting/display
                "updatedAt": row.created_at,
                "lastMessage": (row.content or "")[:100],
            }
            record_ids.add(key)

        # Attach chief complaint from medical record, if available
        for rid in record_ids:
            try:
                rid_uuid = uuid.UUID(rid)
                user_uuid = uuid.UUID(str(request.user_id))
                rec = self.medical_record_repo.get_medical_record_by_id(record_id=rid_uuid, user_id=user_uuid)
                # rec.data is a dict; try to navigate to medical_history.chief_complaint
                data = getattr(rec, "data", {}) or {}
                mh = (data or {}).get("medical_history") or {}
                cc = mh.get("chief_complaint")
                if cc:
                    previews_by_record[rid]["chiefComplaint"] = cc
            except Exception:
                # Ignore if record not found or malformed data
                pass

        # Return as a list, sorted by most recent activity desc (ChatGPT style)
        res = sorted(previews_by_record.values(), key=lambda x: x["updatedAt"], reverse=True)

        return {
            "histories": res
        }
