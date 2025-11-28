# backend/src/app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Global configuration loaded from environment variables.
    Docker Compose passes DATABASE_URL and DATABASE_URL_ASYNC correctly.
    We must NOT override them with localhost defaults.
    """

    # These will now come from the environment (docker-compose)
    database_url: str
    database_url_async: str

    # Secret key for JWT encryption
    secret_key: str = "dev-secret-key-change-me"

    # Optional development override
    dev_admin_secret: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        """Legacy uppercase alias for Alembic."""
        return self.database_url

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
