from app import config as test_module


def test_configs():
    configs = test_module.settings

    assert configs.APP_NAME == "accounting-service"
    assert (
        configs.DB_URI.unicode_string()
        == "postgresql://accounting-service:accounting-service@localhost:3306/accounting-service"
    )
