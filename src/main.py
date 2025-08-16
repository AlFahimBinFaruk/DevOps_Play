from fastapi import FastAPI
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
