from fastapi import APIRouter, Depends, HTTPException,Header
from sqlmodel import Session
from ..db.database import get_session
from .services import create_user, authenticate_user, get_access_token,validate_token,get_current_user
from .schemas import UserCreate, UserLogin, UserRead, TokenValidationResponse, UserInternalRead,TokenValidationRequest
import os


router = APIRouter(prefix="/auth", tags=["auth"])

# Internal api router.
internal_router = APIRouter(prefix="/internal", tags=["internal"])

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

def verify_internal_api_key(api_key:str=Header(...)):
    if api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True




"""
Public Routes.
"""

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


@router.get("/profile")
async def get_user_profile():
    try:
        user = get_current_user()
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))



"""
Internal Routes.
"""

@internal_router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(
    request: TokenValidationRequest, 
    db: Session = Depends(get_session),
    _: bool = Depends(verify_internal_api_key)):
    try:
        user = validate_token(request.token, db)
        return TokenValidationResponse(
            valid=True,
            user_id=user.id,
            username=user.username,
        )
    except Exception as e:
        return TokenValidationResponse(
            valid=False,
            error=str(e),
        )

