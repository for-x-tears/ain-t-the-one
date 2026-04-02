from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Comment
from app.schems import CommentCreate
from uuid import UUID

class CommentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_task(self, task_id: UUID):
        result = await self.db.execute(
            select(Comment).filter(Comment.task_id == task_id)
        )
        return result.scalars().all()

    async def get_by_id(self, comment_id: UUID):
        result = await self.db.execute(
            select(Comment).filter(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, comment_data: CommentCreate, task_id: UUID, owner_id: UUID):
        new_comment = Comment(
            text=comment_data.text,
            task_id=task_id,
            owner_id=owner_id
        )
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment