from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.users import router as users_router
from app.core.config import settings

app = FastAPI(title="Fibrito API")

client = None
db = None


@app.on_event("startup")
async def startup():
    global client, db
    if not settings.mongo_uri:
        raise RuntimeError("MONGO_URI no esta configurado")

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    await db["users"].create_index("email", unique=True)
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
