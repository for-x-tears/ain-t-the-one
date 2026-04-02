from app.repositories.delo_repo import TaskRepository
from app.schems import TaskCreate, TaskUpdate
from uuid import UUID

class TaskService:

    def __init__(self, repo: TaskRepository):
        self.repo = repo

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