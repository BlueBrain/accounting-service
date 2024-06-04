from app import errors as test_module


def test_errors():
    error = test_module.ApiError()

    assert isinstance(error, Exception)
    assert error.status_code == 400
