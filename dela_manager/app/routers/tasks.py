from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID, uuid4

from app.models import Task
from app.storage import tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task)
def create_task(task: Task):
    task.id = uuid4()
    tasks.append(task)
    return task


@router.get("/", response_model=List[Task])
def read_task_list():
    return tasks


@router.get("/{task_id}", response_model=Task)
def read_1task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))
            tasks[idx] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}", response_model=Task)
def delete_task(task_id: UUID):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(idx)
    raise HTTPException(status_code=404, detail="Task not found")
