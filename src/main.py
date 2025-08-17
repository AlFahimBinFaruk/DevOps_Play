from fastapi import FastAPI, APIRouter
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)

from .user.views import router as user_router

app.include_router(user_router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
