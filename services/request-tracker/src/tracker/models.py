from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class RequestLog(SQLModel, table=True):
    __tablename__ = "request_logs"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamp
    timestamp: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
        index=True
    )
    
    # Service info
    service: str = Field(max_length=50, nullable=False, index=True)
    
    # Request info
    method: str = Field(max_length=10, nullable=False)
    path: str = Field(max_length=500, nullable=False, index=True)
    query_params: Optional[str] = Field(default=None, sa_column_kwargs={"type_": "Text"})
    
    # Client info
    client_ip: Optional[str] = Field(default=None, max_length=45)  # IPv6 can be up to 45 chars
    user_agent: Optional[str] = Field(default=None, max_length=500)
    referer: Optional[str] = Field(default=None, max_length=500)
    origin: Optional[str] = Field(default=None, max_length=200)
    
    # Geolocation (from IP)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    
    # User context
    user_id: Optional[int] = Field(default=None, index=True)
    
    # Response info
    status_code: int = Field(nullable=False, index=True)
    duration_ms: float = Field(nullable=False)