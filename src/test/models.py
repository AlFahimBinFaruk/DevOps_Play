from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class TestTwo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    desc: str
