from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Servicio Basico de Prueba")


class Item(BaseModel):
    name: str


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Servicio FastAPI funcionando"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items/{item_id}")
async def get_item(item_id: int) -> dict[str, int]:
    return {"id": item_id}


@app.post("/items")
async def create_item(item: Item) -> dict[str, object]:
    return {"message": "Item recibido", "item": item.model_dump()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.simple_service:app", host="127.0.0.1", port=3000, reload=True)
    print("Servicio FastAPI iniciado en http://localhost:3000")
