"""Logger configuration."""

import logging.config
from pathlib import Path

import yaml

from app.config import configs


def _read_config_file() -> dict | None:
    path = Path(configs.LOGGING_CONFIG)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        L.warning("Logging configuration file not found: %s", path)
        return None


def _configure(logger: logging.Logger | None) -> logging.Logger:
    """Configure logging."""
    assert logger is not None
    if logging_config_dict := _read_config_file():
        logging.config.dictConfig(logging_config_dict)
    if configs.LOGGING_LEVEL:
        logger.setLevel(configs.LOGGING_LEVEL)
    return logger


L = logging.getLogger(__name__).parent
L = _configure(L)
