from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from models.entities.model import Diagnosis
from fastapi import HTTPException
import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class DiagnosisRepo:
    def __init__(self, db: Session):
        self.db = db

    def add_diagnosis(
        self,
        *,
        user_id: UUID,
        record_id: UUID,
        reasoning_process: str,
        diagnosis: dict,
        further_test: list | dict,
    ) -> Diagnosis:
        try:
            row = Diagnosis(
                user_id=user_id,
                record_id=record_id,
                reasoning_process=reasoning_process,
                diagnosis=diagnosis,
                further_test={"items": further_test} if isinstance(further_test, list) else (further_test or {}),
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error adding diagnosis for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error adding diagnosis.") from e

    def get_latest(self, *, user_id: UUID, record_id: UUID) -> Optional[Diagnosis]:
        try:
            stmt = (
                select(Diagnosis)
                .where(Diagnosis.user_id == user_id, Diagnosis.record_id == record_id)
                .order_by(Diagnosis.created_at.desc())
                .limit(1)
            )
            return self.db.exec(stmt).first()
        except SQLAlchemyError as e:
            logger.exception("DB error fetching latest diagnosis for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error fetching diagnosis.") from e

