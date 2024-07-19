from app import logger as test_module
from app.config import settings


def test_logger_configuration():
    try:
        result = test_module.configure_logging()
        assert result == [1]
    finally:
        test_module.L.remove()


def test_logger_with_missing_config(monkeypatch):
    monkeypatch.setattr(settings, "LOGGING_CONFIG", "path/to/missing/config.yaml")
    try:
        result = test_module.configure_logging()
        assert result is None
    finally:
        test_module.L.remove()
