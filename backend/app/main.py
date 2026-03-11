import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.users import router as users_router

app = FastAPI(title="Fibrito API")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "fibrito")

client = None
db = None


@app.on_event("startup")
async def startup():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    app.state.db = db


@app.on_event("shutdown")
async def shutdown():
    if client is not None:
        client.close()


app.include_router(users_router)


@app.get("/api/health")
async def health():
    await db.command("ping")
    return {"status": "ok", "database": "connected"}