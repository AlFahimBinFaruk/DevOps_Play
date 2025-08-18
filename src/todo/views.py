from fastapi import APIRouter, Depends
from ..db.database import get_session
from sqlmodel import Session
from .schemas import TodoCreate, TodoRead
from ..user.models import User
from ..user.services import get_current_user
from .services import create, get_all

router = APIRouter(prefix="/todo", tags=["todo"])


@router.post("/create", response_model=TodoRead)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return create(db, todo, user)


@router.get("/my-todos", response_model=list[TodoRead])
async def get_my_todos(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return get_all(db, user)
