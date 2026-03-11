
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class Task(BaseModel):
    id: Optional[UUID] = None
    title: str = Field(..., min_length=8, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    completed: bool = False
    time: Optional[str] = None
    #я пока что ещё не знаю какой переменной может быть время для выполнения и какое это вообще время
