from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from .schemas import TodoCreate, TodoRead
from .models import Todo
from ..user.models import User


def create(db: Session, new_todo: TodoCreate, user: User) -> TodoRead:
    todo = Todo(**new_todo.model_dump(), owner_id=user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def get_all(db: Session, user: User) -> list[TodoRead]:
    todos = db.exec(select(Todo).where(Todo.owner_id == user.id)).all()
    return todos
