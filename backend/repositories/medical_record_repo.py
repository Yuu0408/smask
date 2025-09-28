from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from models.entities.model import MedicalRecord
from fastapi import HTTPException
import logging
import datetime
from typing import Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)

class MedicalRecordRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_medical_record_by_id(self, record_id: UUID, user_id: UUID) -> MedicalRecord:
        """
        Fetch a record by id, scoped to the owner (user_id).
        Raises 404 if not found and 500 on DB errors.
        """
        try:
            stmt = select(MedicalRecord).where(
                MedicalRecord.record_id == record_id,
                MedicalRecord.user_id == user_id,
            )
            record = self.db.exec(stmt).first()
            if not record:
                raise HTTPException(status_code=404, detail="Medical record not found.")
            logger.info("MedicalRecord retrieved: %s", record_id)
            return record
        except SQLAlchemyError as e:
            logger.exception("DB error retrieving record %s", record_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while retrieving the record.",
            ) from e
        
    def get_latest_record_id(self, user_id: UUID) -> UUID | None:
        """
        Return the most recently created record_id for a given user.
        Returns None if no records exist.
        """
        try:
            stmt = (
                select(MedicalRecord.record_id)
                .where(MedicalRecord.user_id == user_id)
                .order_by(MedicalRecord.created_at.desc())
                .limit(1)
            )
            result = self.db.exec(stmt).first()
            return result  # will be None if no rows
        except SQLAlchemyError as e:
            logger.exception("DB error fetching latest record for user %s", user_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while fetching latest record.",
            ) from e



    def add_record(self, *, user_id: UUID, data: Dict[str, Any]) -> MedicalRecord:
        """
        Create a new record. Timestamps are handled by the model (server defaults).
        Returns the created record.
        """
        try:
            rec = MedicalRecord(user_id=user_id, data=data)
            self.db.add(rec)
            self.db.commit()
            self.db.refresh(rec)
            logger.info("MedicalRecord created: %s (user=%s)", rec.record_id, user_id)
            return rec
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error creating record for user %s", user_id)
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while creating the record.",
            ) from e
    
    def update_record(self, record: MedicalRecord):
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            logger.info(f"record updated successfully: {record.record_id}")
            return record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"SQLAlchemyError while updating record {record.record_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while updating the record."
            )
    
    def update_record_status(self, record: MedicalRecord, status, error_message=None):
        try:
            record.ingress_status = status
            record.update_date = datetime.datetime.now()
            record.error_details = str(error_message)

            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            logger.info(f"Updated record {record.record_id} status to {status} with error: {error_message}")
            return record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating status for record {getattr(record, 'record_id', None)}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while updating record status."
            )