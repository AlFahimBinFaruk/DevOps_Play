from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Request
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

# Make sure to import the model to create tables
from ..user.models import User
from ..todo.models import Todo
from ..test.models import TestTwo

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will execute before the application starts
    engine = create_engine(DATABASE_URL, echo=True)
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Sessionlocal is a factory for new Session objects
    # It is used to create a new session for each request
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=Session
    )

    app.state.SessionLocal = SessionLocal

    yield
    # This will execute after the application stops(because of yield)
    app.state.db.close()
    engine.dispose()


def get_session(request: Request) -> Session:
    # This ultimately invokes the sessionmaker func to create a new session
    SessionLocal = request.app.state.SessionLocal
    if SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session maker not found",
        )
    with SessionLocal() as session:
        yield session
