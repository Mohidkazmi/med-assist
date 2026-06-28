import os
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Medical Scribe Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # CORS configuration - default to allowing local dev servers
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend Next.js default port
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_DB: str = "med_scribe_dev"
    POSTGRES_USER: str = "scribe_admin"
    POSTGRES_PASSWORD: str = "secure_development_password_99"
    POSTGRES_PORT: int = 5433

    @property
    def database_url_async(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Tells pydantic-settings to read variables from the parent directory's .env file
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env variables not defined here
    )


settings = Settings()
