from fastapi import FastAPI
from .db.database import lifespan
import socket
import os

app = FastAPI(lifespan=lifespan)

from .user.views import router as user_router
from .todo.views import router as todo_router

app.include_router(user_router)
app.include_router(todo_router)


@app.get("/")
async def read_root():
    return {"message": "Server Running!"}

@app.get("/info")
async def container_info():
    # These values comes from docker.
    return {
        "container_id": socket.gethostname(),
        "container_name": os.environ.get("HOSTNAME", "unknown"),
        "process_id": os.getpid(),
        "message": f"Response from container: {socket.gethostname()}"
    }