from fastapi import FastAPI
from .db.database import lifespan
import socket
import os

from prometheus_fastapi_instrumentator import Instrumentator
import logging
from logging_loki import LokiHandler


# Loki handler
logger = logging.getLogger("fastapi")
logger.setLevel(logging.INFO)
loki_handler = LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "fastapi_app"},
    version="1",
)
logger.addHandler(loki_handler)

# Initialize app.
app = FastAPI(lifespan=lifespan)

# Prometheus Instrumentator
Instrumentator().instrument(app).expose(app)

from .user.views import router as user_router
from .todo.views import router as todo_router

app.include_router(user_router)
app.include_router(todo_router)


@app.get("/")
async def read_root():
    logger.info("Root endpoint was accessed.")
    return {"message": "Server Running!"}


@app.get("/info")
async def container_info():
    # These values comes from docker.
    return {
        "container_id": socket.gethostname(),
        "container_name": os.environ.get("HOSTNAME", "unknown"),
        "process_id": os.getpid(),
        "message": f"Response from container: {socket.gethostname()}",
    }
