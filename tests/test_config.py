from app import config as test_module


def test_configs():
    configs = test_module.settings

    assert configs.APP_NAME == "accounting-service"
    assert (
        configs.DB_URI == "postgresql+asyncpg://"
        "accounting_service:accounting_service@db:5432/accounting_service"
    )
