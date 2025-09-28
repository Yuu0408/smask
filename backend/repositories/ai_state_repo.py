# repositories/ai_state_repo.py
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import literal_column
from models.entities.model import AIState
from fastapi import HTTPException
import logging
from typing import Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)

class AIStateRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_ai_state(self, record_id: UUID, user_id: UUID) -> AIState:
        try:
            # populate_existing=True forces SQLAlchemy to refresh an already-loaded
            # instance in the identity map with fresh DB values. This avoids stale
            # data after raw upserts in the same session.
            stmt = (
                select(AIState)
                .where(
                    AIState.record_id == record_id,
                    AIState.user_id == user_id,
                )
                .execution_options(populate_existing=True)
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

    # repositories/ai_state_repo.py
    def add_ai_state(self, *, user_id: UUID, record_id: UUID, data: Dict[str, Any]) -> AIState:
        table = AIState.__table__
        stmt = (
            pg_insert(table)
            .values(record_id=record_id, user_id=user_id, data=data)
            .on_conflict_do_update(
                index_elements=[table.c.record_id, table.c.user_id],
                set_={"data": literal_column("EXCLUDED.data")}
            )
            .returning(*table.c)
        )
        # Avoid autoflush surprises during raw SQL
        with self.db.no_autoflush:
            row = self.db.exec(stmt).first()
        # No commit here. Let the service do it.
        # If you want an ORM instance, refetch with the same session (still no commit):
        return self.get_ai_state(record_id=record_id, user_id=user_id)


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
