from pydantic import BaseModel
from typing import Optional


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TodoRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
