"""Configuration."""

from functools import cached_property

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ENV: str = "development"
    API: str = "/api"
    API_V1: str = "/api/v1"
    APP_NAME: str = "accounting-service"
    APP_VERSION: str | None = None
    APP_DEBUG: bool = True
    COMMIT_SHA: str | None = None

    CORS_ORIGINS: list[str] = ["*"]
    LOGGING_CONFIG: str = "app/data/logging.yaml"
    LOGGING_LEVEL: str | None = None

    DB_ENGINE: str = "postgresql"
    DB_USER: str = APP_NAME
    DB_PASS: str = APP_NAME
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = APP_NAME

    @cached_property
    def DB_URI(self) -> PostgresDsn:
        """Return the db uri built from the parameters."""
        return PostgresDsn.build(
            scheme=self.DB_ENGINE,
            username=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )


settings = Settings()
