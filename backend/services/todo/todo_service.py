from sqlmodel import Session
from fastapi import HTTPException
from repositories import TodoRepo
from models.dto.modelDto import (
    GetCurrentTodoRequest,
    GetCurrentTodoResponse,
    UpdateTodoItemRequest,
    UpdateTodoItemResponse,
    TodoItem,
)
from typing import Optional, List

class TodoService:
    def __init__(self, db: Session):
        self.db = db
        self.todo_repo = TodoRepo(db)

    async def get_current_todo(self, request: GetCurrentTodoRequest):
        user_id = request.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail='Invalid user id')

        # If no record_id provided -> use latest record that has todos
        record_id: Optional[str] = request.record_id or None
        if not record_id:
            latest = self.todo_repo.get_latest_record_id_for_user(user_id=user_id)
            if not latest:
                return GetCurrentTodoResponse(user_id=str(user_id), record_id="", items=[])
            record_id = str(latest)

        rows = self.todo_repo.list_todos(user_id=user_id, record_id=record_id)
        items: List[TodoItem] = [TodoItem(text=r.text, is_check=r.is_check) for r in rows]
        return GetCurrentTodoResponse(user_id=str(user_id), record_id=str(record_id), items=items)

    async def update_todo_item(self, request: UpdateTodoItemRequest):
        user_id = request.user_id
        if not user_id:
            raise HTTPException(status_code=400, detail='Invalid user id')

        record_id: Optional[str] = request.record_id or None
        if not record_id:
            latest = self.medical_record_repo.get_latest_record_id(user_id=user_id)
            if not latest:
                raise HTTPException(status_code=404, detail='No record found to update todo')
            record_id = str(latest)

        rows = self.todo_repo.update_todo_checked_by_index(user_id=user_id, record_id=record_id, index=request.index, is_check=request.is_check)
        items: List[TodoItem] = [TodoItem(text=r.text, is_check=r.is_check) for r in rows]
        return UpdateTodoItemResponse(user_id=str(user_id), record_id=str(record_id), items=items)
