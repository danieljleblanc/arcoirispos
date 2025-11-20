from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.models.base import Base  # important fix!

# Create async database engine
engine = create_async_engine(
    settings.database_url_async,
    echo=True,  # Turn off in production
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
