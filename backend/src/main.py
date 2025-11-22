# backend/src/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router

app = FastAPI(
    title="ArcoirisPOS API",
    description="Backend API for Arcoiris POS System",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS (required for frontend to call API)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # adjust for production later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------
app.include_router(api_router, prefix="/api")


# ---------------------------------------------------------
# Custom OpenAPI to enable BearerAuth instead of OAuth2
# ---------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ArcoirisPOS API",
        version="1.0.0",
        description="Backend API for Arcoiris POS System",
        routes=app.routes,
    )

    # 🔥 Add REAL JWT Bearer Authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # 🔥 Apply BearerAuth globally
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
