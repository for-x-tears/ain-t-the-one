from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.database import get_db
from app.schems import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.delo_repo import TaskRepository
from app.services.task_service import TaskService
from app.auth import get_current_user
from app.exceptions import TaskNotFoundException

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)):
    repo = TaskRepository(db)
    return TaskService(repo)


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    return await service.create_task(task_data, owner_id=user_id)


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    return await service.get_all(owner_id=user_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    task = await service.get_by_id(task_id, owner_id=user_id)
    if not task:
        raise TaskNotFoundException()
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    updated = await service.update_task(task_id, task_data, owner_id=user_id)
    if not updated:
        raise TaskNotFoundException()
    return updated


@router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    deleted = await service.delete_task(task_id, owner_id=user_id)
    if not deleted:
        raise TaskNotFoundException()
    return deleted


@router.post(
    "/{task_id}/upload-avatar",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def upload_task_avatar(
    task_id: UUID,
    file: UploadFile = File(...),
    service: TaskService = Depends(get_task_service),
    user_id: UUID = Depends(get_current_user)
):
    """
    Загружает аватарку (изображение) для задачи и возвращает обновлённую задачу с avatar_url
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (jpg, png, gif, etc.)"
        )

    updated_task = await service.upload_avatar(task_id, file, owner_id=user_id)
    
    return updated_task