import asyncio

from services.todo.todo_service import TodoService
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models.dto.modelDto import GetCurrentTodoRequest, GetCurrentTodoResponse, UpdateTodoItemRequest, UpdateTodoItemResponse

router = APIRouter(prefix="/v1/todo")

@router.get("", response_model=GetCurrentTodoResponse)
async def get_todo(request: GetCurrentTodoRequest = Depends(), db: Session = Depends(get_session)):
    service = TodoService(db)
    print(f"Request: {request}")
    result = await service.get_current_todo(request)
    return result

@router.patch("/check", response_model=UpdateTodoItemResponse)
async def check_todo_item(request: UpdateTodoItemRequest, db: Session = Depends(get_session)):
    service = TodoService(db)
    result = await service.update_todo_item(request)
    return result
