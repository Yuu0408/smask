from sqlmodel import Session, select, delete
from sqlalchemy.exc import SQLAlchemyError
from models.entities.model import Todo
from fastapi import HTTPException
import logging
from typing import List, Tuple, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class TodoRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_todos(self, *, user_id: UUID, record_id: UUID) -> List[Todo]:
        try:
            # Exclude placeholders (empty text)
            stmt = (
                select(Todo)
                .where(Todo.user_id == user_id, Todo.record_id == record_id, Todo.text != "")
                .order_by(Todo.position.asc(), Todo.created_at.asc())
            )
            return self.db.exec(stmt).all()
        except SQLAlchemyError as e:
            logger.exception("DB error listing todos for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error listing todos.") from e

    def replace_todos(self, *, user_id: UUID, record_id: UUID, items: List[Tuple[str, bool]]):
        try:
            # clear current
            self.db.exec(delete(Todo).where(Todo.user_id == user_id, Todo.record_id == record_id))
            # insert new
            if not items:
                # insert a placeholder to mark presence for this record
                self.db.add(Todo(user_id=user_id, record_id=record_id, text="", is_check=False, position=0))
            else:
                pos = 0
                for text, is_check in items:
                    row = Todo(user_id=user_id, record_id=record_id, text=text, is_check=bool(is_check), position=pos)
                    pos += 1
                    self.db.add(row)
            self.db.commit()
            return self.list_todos(user_id=user_id, record_id=record_id)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error replacing todos for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error replacing todos.") from e

    def update_todo_checked_by_index(self, *, user_id: UUID, record_id: UUID, index: int, is_check: bool) -> List[Todo]:
        try:
            rows = self.list_todos(user_id=user_id, record_id=record_id)
            if index < 0 or index >= len(rows):
                raise HTTPException(status_code=400, detail="Todo index out of range")
            target = rows[index]
            target.is_check = bool(is_check)
            self.db.add(target)
            self.db.commit()
            self.db.refresh(target)
            return self.list_todos(user_id=user_id, record_id=record_id)
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.exception("DB error updating todo check for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error updating todo.") from e

    def get_latest_record_id_for_user(self, *, user_id: UUID) -> Optional[UUID]:
        try:
            # pick the record_id that has most recent todo
            from sqlalchemy import func
            stmt = (
                select(Todo.record_id, func.max(Todo.created_at).label("latest"))
                .where(Todo.user_id == user_id)
                .group_by(Todo.record_id)
                .order_by(func.max(Todo.created_at).desc())
                .limit(1)
            )
            row = self.db.exec(stmt).first()
            return row[0] if row else None
        except SQLAlchemyError as e:
            logger.exception("DB error getting latest record_id from todos for user %s", user_id)
            raise HTTPException(status_code=500, detail="Database error.") from e
