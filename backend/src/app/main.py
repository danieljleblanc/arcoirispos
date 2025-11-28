# backend/src/app/main.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

# ✔ This is correct for your project structure
from src.app.api_router import api_router


# ---------------------------------------------------------
# FASTAPI INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(
    title="ArcoirisPOS API",
    description="Backend API for Arcoiris POS System",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS (development defaults)
# ---------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "*",  # (optional during dev)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTERS (all mounted under /api via api_router)
# ---------------------------------------------------------
app.include_router(api_router)


# ---------------------------------------------------------
# CUSTOM OPENAPI — JWT Bearer Auth
# ---------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override generator
app.openapi = custom_openapi
