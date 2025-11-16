from fastapi import FastAPI
from .db.database import lifespan

app=FastAPI(lifespan=lifespan)

@app.on_event("startup")
async def startup_event():
    print("✅ Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("✅ Shutting down...")

