from fastapi import FastAPI

app = FastAPI(title = "Fibrito API")

@app.get("/api/health")
async def health():
    return {"status": "ok"}