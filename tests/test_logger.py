import logging

from app import logger as test_module
from app.config import settings


def test_logger_without_overriding_level(monkeypatch):
    monkeypatch.setattr(settings, "LOGGING_LEVEL", None)
    logger = test_module._configure("test")

    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.NOTSET

    # uvicorn handlers are set from the config file
    assert len(logging.getLogger("uvicorn").handlers) > 0


def test_logger_with_overriding_level(monkeypatch):
    monkeypatch.setattr(settings, "LOGGING_LEVEL", "ERROR")
    logger = test_module._configure("test")

    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.ERROR


def test_logger_with_missing_config(monkeypatch):
    monkeypatch.setattr(settings, "LOGGING_CONFIG", "path/to/missing/config.yaml")
    logger = test_module._configure("test")

    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG
