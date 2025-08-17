from sqlmodel import SQLModel, select, Session
from fastapi.security import OAuth2PasswordBearer
from .models import User
from ..core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from ..db.database import get_session

from fastapi import HTTPException, Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def get_access_token(user: User) -> str:
    return {
        "access_token": create_access_token(data={"user_id": user.id}),
        "token_type": "bearer",
    }


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    user = db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
