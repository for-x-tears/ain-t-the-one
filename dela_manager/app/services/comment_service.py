from app.repositories.comment_repo import CommentRepository
from app.repositories.delo_repo import TaskRepository
from app.schems import CommentCreate
from uuid import UUID

class CommentService:

    def __init__(self, comment_repo: CommentRepository, task_repo: TaskRepository):
        self.comment_repo = comment_repo
        self.task_repo = task_repo

    def get_all(self, task_id: UUID, owner_id: UUID):
        # сначала проверяем что задача существует и принадлежит этому юзеру
        task = self.task_repo.get_by_id(task_id, owner_id)
        if not task:
            return None
        return self.comment_repo.get_all_by_task(task_id)

    def create(self, comment_data: CommentCreate, task_id: UUID, owner_id: UUID):
        task = self.task_repo.get_by_id(task_id, owner_id)
        if not task:
            return None
        return self.comment_repo.create(comment_data, task_id, owner_id)