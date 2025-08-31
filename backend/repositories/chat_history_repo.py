from models.entities.model import ChatHistory
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
import datetime
from typing import Dict, Any
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
    
    def add_message(self, *, user_id: UUID, record_id: UUID, role: str, content: str) -> ChatHistory:
        """
        Create a new record. Timestamps are handled by the model (server defaults).
        Returns the created record.
        """
        try:
            message = ChatHistory(user_id=user_id, record_id=record_id, role=role, content=content)
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            logger.info("Message created: %s (user=%s)", message.record_id, user_id)
            return message
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error creating record for user %s", user_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while creating the record.",
            ) from e