from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

# Make sure to import the model to create tables
from .. import model

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app.state.db = SessionLocal()

    yield

    app.state.db.close()
    engine.dispose()
