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

    UVICORN_PORT: int = 8000

    CORS_ORIGINS: list[str] = ["*"]
    LOGGING_CONFIG: str = "app/data/logging.yaml"

    SQS_STORAGE_QUEUE_NAME: str = "storage.fifo"
    SQS_SHORT_JOBS_QUEUE_NAME: str = "short-jobs.fifo"
    SQS_LONG_JOBS_QUEUE_NAME: str = "long-jobs.fifo"
    SQS_CLIENT_ERROR_SLEEP: float = 10

    DB_ENGINE: str = "postgresql+asyncpg"
    DB_USER: str = "accounting_service"
    DB_PASS: str = "accounting_service"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "accounting_service"

    DB_POOL_SIZE: int = 30
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
