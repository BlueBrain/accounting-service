from app import models as test_module


def test_models():
    assert test_module.Transactions
    assert test_module.VlabTopup
