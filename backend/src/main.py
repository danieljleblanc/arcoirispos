# backend/src/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router


# ---------------------------------------------------------
# FASTAPI INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(
    title="ArcoirisPOS API",
    description="Backend API for Arcoiris POS System",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS (development defaults — tighten in production)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Change to explicit origins before launch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTERS: unified /api prefix (matches routes.py)
# ---------------------------------------------------------
app.include_router(api_router)


# ---------------------------------------------------------
# CUSTOM OPENAPI — JWT Bearer Authentication (global)
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

    # Add JWT Bearer scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply globally to all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override FastAPI OpenAPI generator
app.openapi = custom_openapi
