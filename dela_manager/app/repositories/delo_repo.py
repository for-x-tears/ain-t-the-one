from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Task
from app.schems import TaskCreate, TaskUpdate
from uuid import UUID

class TaskRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, owner_id: UUID):
        result = await self.db.execute(
            select(Task).filter(Task.owner_id == owner_id)
        )
        return result.scalars().all()

    async def get_by_id(self, task_id: UUID, owner_id: UUID):
        result = await self.db.execute(
            select(Task).filter(Task.id == task_id, Task.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def create(self, task_data: TaskCreate, owner_id: UUID):
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            owner_id=owner_id
        )
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def update(self, task_id: UUID, task_data: TaskUpdate, owner_id: UUID):
        task = await self.get_by_id(task_id, owner_id)
        if not task:
            return None
        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(task, field, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: UUID, owner_id: UUID):
        task = await self.get_by_id(task_id, owner_id)
        if not task:
            return None
        await self.db.delete(task)
        await self.db.commit()
        return task