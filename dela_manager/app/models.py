from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Task(BaseModel):
    id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    time: Optional[str] = None
    #я пока что ещё не знаю какой переменной может быть время для выполнения и какое это вообще время
