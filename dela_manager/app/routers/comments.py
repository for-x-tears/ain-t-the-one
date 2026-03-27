from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schems import CommentCreate, CommentResponse
from app.repositories.comment_repo import CommentRepository
from app.repositories.delo_repo import TaskRepository
from app.services.comment_service import CommentService
from app.auth import get_current_user
from app.exceptions import TaskNotFoundException

router = APIRouter(prefix="/tasks", tags=["comments"])

def get_comment_service(db: Session = Depends(get_db)):
    comment_repo = CommentRepository(db)
    task_repo = TaskRepository(db)
    return CommentService(comment_repo, task_repo)

@router.post("/{task_id}/comments", response_model=CommentResponse)
def create_comment(task_id: UUID, comment_data: CommentCreate, service: CommentService = Depends(get_comment_service), user_id: UUID = Depends(get_current_user)):
    result = service.create(comment_data, task_id, owner_id=user_id)
    if not result:
        raise TaskNotFoundException()
    return result

@router.get("/{task_id}/comments", response_model=List[CommentResponse])
def get_comments(task_id: UUID, service: CommentService = Depends(get_comment_service), user_id: UUID = Depends(get_current_user)):
    result = service.get_all(task_id, owner_id=user_id)
    if result is None:
        raise TaskNotFoundException()
    return result