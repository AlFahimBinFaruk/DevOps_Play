from sqlmodel import select, Session, func
from .models import RequestLog
from .schemas import RequestTrackingMessage
from datetime import datetime
from typing import List, Dict, Optional

def create_request_log(
        db: Session,
        message: RequestTrackingMessage,
        geo_data: Dict[str,Optional[str]]
    ) -> RequestLog:
    
    request_log = RequestLog(
        timestamp=datetime.fromisoformat(message.timestamp),
        service=message.service,
        method=message.method,
        path=message.path,
        query_params=message.query_params,
        client_ip=message.client_ip,
        user_agent=message.user_agent,
        referer=message.referer,
        origin=message.origin,
        country=geo_data.get("country"),
        city=geo_data.get("city"),
        latitude=geo_data.get("latitude"),
        longitude=geo_data.get("longitude"),
        user_id=message.user_id,
        status_code=message.status_code,
        duration_ms=message.duration_ms
    )

    db.add(request_log)
    db.commit()
    db.refresh(request_log)
    return request_log



def get_request_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    service: Optional[str] = None # ums,note
) -> List[RequestLog]:
    query = select(RequestLog)
    if service:
        query = query.where(RequestLog.service == service)
    query=query.offset(skip).limit(limit).order_by(RequestLog.timestamp.desc())
    return db.exec(query).all()



def get_request_log_by_id(
    db: Session,
    log_id: int
) -> List[RequestLog]:
    query = select(RequestLog)
    query = query.where(RequestLog.id == log_id)
    return db.exec(query).first()


def get_error_logs(
    db: Session,
    limit: int = 100
) -> List[RequestLog]:
    query = select(RequestLog)
    query = query.where(RequestLog.status_code>=400).limit(limit).order_by(RequestLog.timestamp.desc())
    return db.exec(query).all()


def get_request_stats(
    db: Session,
    service: Optional[str] = None
)->Dict:
    query = select(
        func.count(RequestLog.id).label("total_requests"),
        func.avg(RequestLog.duration_ms).label("avg_duration_ms"),
        func.sum(func.case((RequestLog.status_code>=400,1),else_=0)).label("error_count"),
        func.sum(func.case((RequestLog.status_code<400,1),else_=0)).label("success_count")
    )
    if service:
        query=query.where(RequestLog.service == service)
    result=db.exec(query).first()

    return {
        "total_requests": result[0] or 0,
        "avg_duration_ms": float(result[1] or 0),
        "error_count": result[2] or 0,
        "success_count": result[3] or 0
    }