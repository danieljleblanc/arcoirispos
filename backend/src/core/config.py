from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Sync DB URL (used by Alembic and anything using psycopg2)
    database_url: str = (
        "postgresql://arcoiris_user:ArcoirisDevP@ss2025@postgres:5432/arcoirispos_dev"
    )

    # Async DB URL (used by SQLAlchemy async engine + asyncpg)
    database_url_async: str = (
        "postgresql+asyncpg://arcoiris_user:ArcoirisDevP@ss2025@postgres:5432/arcoirispos_dev"
    )

    class Config:
        env_file = ".env"


# Instantiate settings
settings = Settings()
