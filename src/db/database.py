from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Request
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

# Make sure to import the model to create tables
from ..user.models import User
from ..todo.models import Todo

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=Session
    )

    app.state.SessionLocal = SessionLocal

    yield

    app.state.db.close()
    engine.dispose()


def get_session(request: Request) -> Session:
    SessionLocal = request.app.state.SessionLocal
    if SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session maker not found",
        )
    with SessionLocal() as session:
        yield session
