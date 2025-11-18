from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.database import database_lifespan
from .consumer.rabbitmq_consumer import RabbitMQConsumer
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger=logging.getLogger(__name__)

def start_consumer():
    try:
        consumer=RabbitMQConsumer()
        consumer.connect()
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"❌ Error starting consumer: {e}")
        raise


# FastAPI gives control to context manager.
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # nested context manager.
    async with database_lifespan(app):
        consumer_thread=threading.Thread(
            target=start_consumer,
            daemon=True, # thread dies when the main app dies.
            name="RabbitMQ-Consumer"
        )
        consumer_thread.start()

        # Control returns to the context manager caller(FastAPI runtime)
        # Surrender the control.
        yield



app=FastAPI(lifespan=app_lifespan)

@app.get("/")
def get_hello():
    return {"message": "Request Tracker Server Running!"}


