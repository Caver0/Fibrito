from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
#Para conectar con MongoDB de forma asíncrona
import os


app = FastAPI(title = "Fibrito API")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = None
db = None
@app.on_event("startup")
async def startup():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]

@app.on_event("shutdown")
async def shutdown():
    client.close()


@app.get("/api/health")
async def health():
    await db.command("ping")
    return {"status": "ok", "database": "connected"}
