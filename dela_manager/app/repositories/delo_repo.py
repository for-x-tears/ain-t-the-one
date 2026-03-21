from sqlalchemy.orm import Session
from app.models import Task
from app.schems import TaskCreate, TaskUpdate
from uuid import UUID

class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, owner_id: UUID):
        return self.db.query(Task).filter(Task.owner_id == owner_id).all()

    def get_by_id(self, task_id: UUID, owner_id: UUID):
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.owner_id == owner_id
        ).first()

    def create(self, task_data: TaskCreate, owner_id: UUID):
        
        
        
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            owner_id=owner_id
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def update(self, task_id: UUID, task_data: TaskUpdate, owner_id: UUID):
        task = self.get_by_id(task_id, owner_id)
        if not task:
            return None
        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: UUID, owner_id: UUID):
        task = self.get_by_id(task_id, owner_id)
        if not task:
            return None
        self.db.delete(task)
        self.db.commit()
        return task