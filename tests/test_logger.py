import logging
import re

from app import logger as test_module
from app.config import settings


def test_logger_configuration():
    test_module.configure_logging()

    logger = test_module.get_logger("app")
    assert logger.level == logging.DEBUG

    logger = test_module.get_logger("root")
    assert logger.level == logging.INFO


def test_logger_with_missing_config(monkeypatch, caplog):
    monkeypatch.setattr(settings, "LOGGING_CONFIG", "path/to/missing/config.yaml")
    test_module.configure_logging()
    pattern = "Logging configuration file not found: .*/path/to/missing/config.yaml"
    assert re.search(pattern, caplog.text)
