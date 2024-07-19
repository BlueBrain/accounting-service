"""Logger configuration."""

import inspect
import json
import logging
import traceback
from pathlib import Path

import loguru
import yaml
from loguru import logger as L  # noqa: N812
from loguru_config import LoguruConfig

from app.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward Loguru sinks.

    See https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging.
    """

    def emit(self, record: logging.LogRecord) -> None:  # noqa: PLR6301
        """Emit a log record."""
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = L.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        L.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def json_formatter(record: "loguru.Record") -> str:
    """Format a log record including only a subset of fields.

    See https://loguru.readthedocs.io/en/stable/resources/recipes.html.
    """

    def _exception_to_dict(ex: "loguru.RecordException") -> dict[str, str | None]:
        return {
            "type": ex.type.__name__ if ex.type else None,
            "value": str(ex.value) if ex.value else None,
            "traceback": "".join(traceback.format_tb(ex.traceback)),
        }

    def _serialize(rec: "loguru.Record") -> str:
        subset = {
            "time": rec["time"].isoformat(),
            "level": rec["level"].name,
            "name": rec["name"],
            "message": rec["message"],
            "extra": rec["extra"],
            "exception": _exception_to_dict(rec["exception"]) if rec["exception"] else None,
        }
        return json.dumps(subset, separators=(",", ":"), default=str)

    # Return the string to be formatted, not the actual message to be logged
    record["extra"]["serialized"] = _serialize(record)
    return "{extra[serialized]}\n"


def configure_logging() -> list[int] | None:
    """Configure logging.

    Returns:
        A list containing the identifiers of added sinks (if any).
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    path = Path(__file__).parents[1] / settings.LOGGING_CONFIG
    if not path.is_file():
        L.warning("Logging not configured, the config file {} doesn't exist", path)
        return None
    config_dict = yaml.safe_load(path.read_bytes())
    for logger_name, logger_level in config_dict.pop("standard_loggers", {}).items():
        logging.getLogger(logger_name).setLevel(logger_level)
    config = LoguruConfig.load(config_dict, configure=False)
    ids = config.parse().configure()
    L.info("Logging configured")
    return ids
