from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schems import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.delo_repo import TaskRepository
from app.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    repo = TaskRepository(db)
    return repo.create(task_data, owner_id=user_id)

@router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    repo = TaskRepository(db)
    return repo.get_all(owner_id=user_id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id, owner_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, task_data: TaskUpdate, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    repo = TaskRepository(db)
    updated = repo.update(task_id, task_data, owner_id=user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task(task_id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    repo = TaskRepository(db)
    deleted = repo.delete(task_id, owner_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted