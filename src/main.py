from fastapi import FastAPI
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)

from .user.views import router as user_router
from .todo.views import router as todo_router

app.include_router(user_router)
app.include_router(todo_router)


@app.get("/")
async def read_root():
    return {"message": "Server Running!"}
