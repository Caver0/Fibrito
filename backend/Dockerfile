FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  
#Instala las dependencias de fastapi y uvicorn

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#Arranca el servidor de FastAPI en el puerto 8000 y lo hace accesible desde cualquier dirección IP.




