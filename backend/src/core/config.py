from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://arcoiris_user:password@postgres:5432/arcoirispos_dev"

    class Config:
        env_file = ".env"

settings = Settings()
