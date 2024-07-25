from app import errors as test_module


def test_errors():
    error = test_module.ApiError(
        message="Test error",
        error_code=test_module.ApiErrorCode.INVALID_REQUEST,
    )

    assert isinstance(error, Exception)
    assert error.message == "Test error"
    assert error.error_code == "INVALID_REQUEST"
    assert error.http_status_code == 400
    assert error.details is None

    assert repr(error) == (
        "ApiError(message='Test error', error_code=INVALID_REQUEST, "
        "http_status_code=400, details=None)"
    )
