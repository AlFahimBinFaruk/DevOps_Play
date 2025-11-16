from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Request
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

from ..tracker.models import RequestLog

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for database initialization
    This executes before the application starts and after it stops
    """
    # This will execute before the application starts
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully")

    # SessionLocal is a factory for new Session objects
    # It is used to create a new session for each request
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=Session
    )

    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    yield
    
    # This will execute after the application stops (because of yield)
    engine.dispose()
    print("✅ Database connection closed")


def get_session(request: Request = None) -> Session:
    """
    Dependency to get database session
    Can be used with or without FastAPI request context
    """
    if request:
        # Used in FastAPI endpoints
        SessionLocal = request.app.state.SessionLocal
        if SessionLocal is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session maker not found",
            )
        with SessionLocal() as session:
            yield session
    else:
        # Used in standalone consumer (no FastAPI request context)
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine, class_=Session
        )
        with SessionLocal() as session:
            yield session