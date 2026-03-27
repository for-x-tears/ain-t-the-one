from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schems import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.delo_repo import TaskRepository
from app.services.task_service import TaskService
from app.auth import get_current_user
from app.exceptions import TaskNotFoundException

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_task_service(db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    return TaskService(repo)

@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, service: TaskService = Depends(get_task_service), user_id: UUID = Depends(get_current_user)):
    return service.create_task(task_data, owner_id=user_id)

@router.get("/", response_model=List[TaskResponse])
def get_tasks(service: TaskService = Depends(get_task_service), user_id: UUID = Depends(get_current_user)):
    return service.get_all(owner_id=user_id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, service: TaskService = Depends(get_task_service), user_id: UUID = Depends(get_current_user)):
    task = service.get_by_id(task_id, owner_id=user_id)
    if not task:
        raise TaskNotFoundException()
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task_data: TaskUpdate, service: TaskService = Depends(get_task_service), user_id: UUID = Depends(get_current_user)):
    updated = service.update_task(task_id, task_data, owner_id=user_id)
    if not updated:
        raise TaskNotFoundException()
    return updated

@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task(task_id: UUID, service: TaskService = Depends(get_task_service), user_id: UUID = Depends(get_current_user)):
    deleted = service.delete_task(task_id, owner_id=user_id)
    if not deleted:
        raise TaskNotFoundException()
    return deleted