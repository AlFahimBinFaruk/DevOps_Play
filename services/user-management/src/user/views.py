from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..db.database import get_session
from .services import create_user, authenticate_user, get_access_token
from .schemas import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register_user(user: UserCreate, db: Session = Depends(get_session)):
    return create_user(db, user.username, user.password)


@router.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_session)):
    user = authenticate_user(db, user.username, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = get_access_token(user)
    return {"user": user, "access_token": access_token}
