from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from models.entities.model import AIState
from fastapi import HTTPException
import logging
import datetime
from typing import Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)

class AIStateRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_ai_state(self, record_id: UUID, user_id: UUID) -> AIState:
        """
        Fetch a record by id, scoped to the owner (user_id).
        Raises 404 if not found and 500 on DB errors.
        """
        try:
            stmt = select(AIState).where(
                AIState.record_id == record_id,
                AIState.user_id == user_id,
            )
            state = self.db.exec(stmt).first()
            if not state:
                raise HTTPException(status_code=404, detail="AI State not found.")
            logger.info("AI State retrieved: %s", record_id)
            return state
        except SQLAlchemyError as e:
            logger.exception("DB error retrieving state %s", record_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while retrieving the state.",
            ) from e

    def add_ai_state(self, *, user_id: UUID, record_id: UUID, data: Dict[str, Any]) -> AIState:
        """
        Create a new record. Timestamps are handled by the model (server defaults).
        Returns the created record.
        """
        try:
            state = AIState(user_id=user_id, record_id=record_id, data=data)
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
            logger.info("AIState created: %s (user=%s)", state.record_id, user_id)
            return state
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error creating record for user %s", user_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while creating the record.",
            ) from e
    
    def update_state(self, state: AIState):
        try:
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
            logger.info(f"state updated successfully: {state.record_id}")
            return state
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"SQLAlchemyError while updating state {state.record_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while updating the state."
            )