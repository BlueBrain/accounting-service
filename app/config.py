"""Configuration."""

from decimal import Decimal

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
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
    DB_URI: str = ""

    DB_POOL_SIZE: int = 30
    DB_POOL_PRE_PING: bool = True
    DB_MAX_OVERFLOW: int = 0

    @field_validator("DB_URI", mode="before")
    @classmethod
    def build_db_uri(cls, v: str, info: ValidationInfo) -> str:
        """Return the configured db uri, or build it from the parameters."""
        if v:
            dsn = PostgresDsn(v)
        else:
            dsn = PostgresDsn.build(
                scheme=info.data["DB_ENGINE"],
                username=info.data["DB_USER"],
                password=info.data["DB_PASS"],
                host=info.data["DB_HOST"],
                port=info.data["DB_PORT"],
                path=info.data["DB_NAME"],
            )
        return dsn.unicode_string()


settings = Settings()
