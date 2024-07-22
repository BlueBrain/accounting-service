"""Configuration."""

from decimal import Decimal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
    )

    ENVIRONMENT: str = "dev"
    APP_NAME: str = "accounting-service"
    APP_VERSION: str | None = None
    APP_DEBUG: bool = False
    COMMIT_SHA: str | None = None

    UVICORN_PORT: int = 8000

    CORS_ORIGINS: list[str] = ["*"]

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    LOG_SERIALIZE: bool = True
    LOG_BACKTRACE: bool = False
    LOG_DIAGNOSE: bool = False
    LOG_ENQUEUE: bool = False
    LOG_CATCH: bool = True
    LOG_STANDARD_LOGGER: dict[str, str] = {"root": "INFO"}

    CHARGE_STORAGE_LOOP_SLEEP: float = 60
    CHARGE_STORAGE_ERROR_SLEEP: float = 60
    CHARGE_STORAGE_MIN_CHARGING_INTERVAL: float = 3600
    CHARGE_STORAGE_MIN_CHARGING_AMOUNT: Decimal = Decimal("0.000001")

    CHARGE_LONG_JOBS_LOOP_SLEEP: float = 60
    CHARGE_LONG_JOBS_ERROR_SLEEP: float = 60
    CHARGE_LONG_JOBS_MIN_CHARGING_INTERVAL: float = 10
    CHARGE_LONG_JOBS_MIN_CHARGING_AMOUNT: Decimal = Decimal("0.000001")

    CHARGE_SHORT_JOBS_LOOP_SLEEP: float = 60
    CHARGE_SHORT_JOBS_ERROR_SLEEP: float = 60

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
