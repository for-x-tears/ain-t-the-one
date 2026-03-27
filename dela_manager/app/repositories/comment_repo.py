from sqlalchemy.orm import Session
from app.models import Comment
from app.schems import CommentCreate
from uuid import UUID

class CommentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_by_task(self, task_id: UUID):
        # выбираю все комментарии под конкретную задачу 
        return self.db.query(Comment).filter(Comment.task_id == task_id).all()

    def get_by_id(self, comment_id: UUID):
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def create(self, comment_data: CommentCreate, task_id: UUID, owner_id: UUID):
        new_comment = Comment(
            text=comment_data.text,
            task_id=task_id,
            owner_id=owner_id
        )
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        return new_comment