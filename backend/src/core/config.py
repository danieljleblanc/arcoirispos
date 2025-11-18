from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Sync DB URL (used by Alembic and any sync engine)
    database_url: str = (
        "postgresql://arcoiris_user:ArcoirisDevP%40ss2025@localhost:5432/arcoirispos_dev"
    )

    # Async DB URL (used by SQLAlchemy async engine + asyncpg)
    database_url_async: str = (
        "postgresql+asyncpg://arcoiris_user:ArcoirisDevP%40ss2025@localhost:5432/arcoirispos_dev"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Provide legacy uppercase name expected by Alembic."""
        return self.database_url

    class Config:
        env_file = ".env"


settings = Settings()
