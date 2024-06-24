"""Logger configuration."""

import logging
import logging.config
from pathlib import Path

import yaml

from app.config import settings


def _read_config_file(path: Path) -> dict | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logging.warning("Logging configuration file not found: %s", path)
        return None


def _configure_logging() -> None:
    """Configure logging."""
    path = Path(__file__).parents[1] / settings.LOGGING_CONFIG
    if logging_config_dict := _read_config_file(path):
        logging.config.dictConfig(logging_config_dict)


def get_logger(name: str) -> logging.Logger:
    """Return a logger based on the given name."""
    return logging.getLogger(name)


_configure_logging()
