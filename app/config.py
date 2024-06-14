"""Configuration."""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ENVIRONMENT: str = "dev"
    APP_NAME: str = "accounting-service"
    APP_VERSION: str | None = None
    APP_DEBUG: bool = False
    COMMIT_SHA: str | None = None

    CORS_ORIGINS: list[str] = ["*"]
    LOGGING_CONFIG: str = "app/data/logging.yaml"
    LOGGING_LEVEL: str | None = None

    DB_ENGINE: str = "postgresql+asyncpg"
    DB_USER: str = "accounting_service"
    DB_PASS: str = "accounting_service"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "accounting_service"

    DB_ECHO: bool = False
    DB_ECHO_POOL: bool = False
    DB_POOL_SIZE: int = 5
    DB_POOL_PRE_PING: bool = True
    DB_MAX_OVERFLOW: int = 0

    @property
    def DB_URI(self) -> str:
        """Return the db uri built from the parameters."""
        return PostgresDsn.build(
            scheme=self.DB_ENGINE,
            username=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        ).unicode_string()


settings = Settings()
