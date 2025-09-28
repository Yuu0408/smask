from models.entities.model import ChatHistory
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
import datetime
from typing import Dict, Any, Optional, Sequence
from uuid import UUID

logger = logging.getLogger(__name__)

class ChatHistoryRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_chat_history(self, record_id: UUID, user_id: UUID) -> ChatHistory:
        try:
            stmt = (
                select(ChatHistory)
                .where(ChatHistory.record_id == record_id, ChatHistory.user_id == user_id)
                .order_by(ChatHistory.created_at.asc())
            )
            return self.db.exec(stmt).all()
        except SQLAlchemyError as e:
            logger.exception("DB error retrieving record %s", record_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while retrieving the record.",
            ) from e
        
    def get_all_chat_history(self, user_id: UUID) -> ChatHistory:
        try:
            stmt = (
                select(ChatHistory)
                .where(ChatHistory.user_id == user_id)
                .order_by(ChatHistory.created_at.asc())
            )
            return self.db.exec(stmt).all()
        except SQLAlchemyError as e:
            logger.exception("DB error retrieving chat history for user %s", user_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while retrieving the chat history.",
            ) from e
    
    def add_messages(
        self,
        *,
        user_id: UUID,
        record_id: UUID,
        messages: Sequence[dict],  # [{"role": "user", "content": "..."} , ...]
        return_rows: bool = False,
    ) -> Optional[list[ChatHistory]]:
        if not messages:
            raise HTTPException(status_code=400, detail="messages must be non-empty")
        try:
            rows: list[ChatHistory] = []
            for msg in messages:
                role = msg.get("role")
                content = (msg.get("content") or "").strip()
                if role not in {"human", "ai", "system"}:
                    raise HTTPException(status_code=400, detail=f"invalid role: {role}")
                if not content:
                    raise HTTPException(status_code=400, detail="content cannot be empty")

                row = ChatHistory(
                    user_id=user_id,
                    record_id=record_id,
                    role=role,
                    content=content,
                    # do NOT set created_at; let DB server_default handle it
                )
                self.db.add(row)
                rows.append(row)

                # If you want DB-generated fields on the objects now:
            self.db.commit()
            if return_rows:
                self.db.flush()  # assign PKs
                for r in rows:
                    # pull server_default columns like created_at
                    self.db.refresh(r, attribute_names=["id", "created_at"])
                return rows

            return None  # success, nothing to return
        except HTTPException:
            # bubble up request errors without logging as 500
            raise
        except SQLAlchemyError as e:
            logger.exception("DB error creating messages for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error occurred.") from e