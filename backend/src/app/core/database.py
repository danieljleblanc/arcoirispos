# backend/src/app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings
from src.app.core.base import Base


# =============================================================
# ASYNC ENGINE (SQLAlchemy 2.x mode recommended)
# =============================================================
engine = create_async_engine(
    settings.database_url_async,
    echo=True,        # Turn off in production
    future=True,      # Explicit 2.0 API behavior
)


# =============================================================
# ASYNC SESSION FACTORY
# =============================================================
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =============================================================
# FASTAPI DEPENDENCY
# =============================================================
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


# =============================================================
# REQUIRED FOR ALEMBIC (env.py autogenerate)
# =============================================================
# Alembic imports this file and expects:
#   from src.app.core.database import Base, engine
metadata = Base.metadata
