# backend/src/main.py

from fastapi import FastAPI

from src.api.routes import api_router

app = FastAPI(title="ArcoirisPOS API")

app.include_router(api_router, prefix="/api")
