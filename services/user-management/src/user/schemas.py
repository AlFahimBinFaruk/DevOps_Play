from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


"""
Internal api schema for S2S.
"""

class UserInternalRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class TokenValidationRequest(BaseModel):
    token: str


class TokenValidationResponse(BaseModel):
    valid:bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    error: Optional[str] = None