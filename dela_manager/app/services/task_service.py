from app.repositories.delo_repo import TaskRepository
from app.schems import TaskCreate, TaskUpdate
from app.services.minio_service import MinioService
from fastapi import UploadFile, HTTPException, status
from uuid import UUID

class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo
        self.minio_service = MinioService()

    async def get_all(self, owner_id: UUID):
        return await self.repo.get_all(owner_id)

    async def get_by_id(self, task_id: UUID, owner_id: UUID):
        return await self.repo.get_by_id(task_id, owner_id)

    async def create_task(self, task_data: TaskCreate, owner_id: UUID):
        return await self.repo.create(task_data, owner_id)

    async def update_task(self, task_id: UUID, task_data: TaskUpdate, owner_id: UUID):
        task = await self.repo.get_by_id(task_id, owner_id)
        if not task:
            return None
        return await self.repo.update(task_id, task_data, owner_id)

    async def delete_task(self, task_id: UUID, owner_id: UUID):
        task = await self.repo.get_by_id(task_id, owner_id)
        if not task:
            return None
        return await self.repo.delete(task_id, owner_id)

    
    async def upload_avatar(self, task_id: UUID, file: UploadFile, owner_id: UUID):
        task = await self.repo.get_by_id(task_id, owner_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission"
            )

        
        avatar_url = await self.minio_service.upload_avatar(file, str(task_id))

        
        updated_task = await self.repo.update_avatar_url(task_id, avatar_url, owner_id)
        
        return updated_task