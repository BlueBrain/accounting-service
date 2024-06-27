from app import config as test_module


def test_configs():
    configs = test_module.settings

    assert configs.APP_NAME == "accounting-service"
    assert (
        "postgresql+asyncpg://accounting_service:accounting_service@"
        f"{configs.DB_HOST}:{configs.DB_PORT}/accounting_service"
    ) == configs.DB_URI
