from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="ArcoirisPOS API")

@app.get("/")
def home():
    return {"message": "ArcoirisPOS Backend is Running!"}

app.include_router(router)
