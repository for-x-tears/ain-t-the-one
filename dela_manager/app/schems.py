from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
class UserResponse(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: bool = False
    # я пока не знаю какой тип у времени и что это вообще за время


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    completed: bool
    owner_id: UUID

    class Config:
        from_attributes = True
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None
    

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: UUID
    text: str
    task_id: UUID
    owner_id: UUID

    class Config:
        from_attributes = True