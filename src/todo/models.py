from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="todos")
