from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RequestTrackingMessage(BaseModel):
    """
    Pydantic model for RabbitMQ message validation
    This validates incoming messages from the queue
    """
    timestamp: str
    service: str
    method: str
    path: str
    query_params: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    origin: Optional[str] = None
    user_id: Optional[int] = None
    status_code: int
    duration_ms: float


class RequestLogRead(BaseModel):
    """Schema for reading request logs (API responses)"""
    id: int
    timestamp: datetime
    service: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    user_id: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None

    class Config:
        from_attributes = True


class RequestLogStats(BaseModel):
    """Schema for aggregate statistics"""
    total_requests: int
    avg_duration_ms: float
    error_count: int
    success_count: int