from app import logger as test_module


def test_logger_configuration():
    try:
        handler_id = test_module.configure_logging()
        assert handler_id == 1
    finally:
        test_module.L.remove()
