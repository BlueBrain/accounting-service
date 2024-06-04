"""Api exceptions."""

from http import HTTPStatus


class ApiError(Exception):
    """Error that should be returned to the client."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the exception and ensure that `status_code` is set."""
        self.status_code = int(kwargs.pop("status_code", HTTPStatus.BAD_REQUEST))
        super().__init__(*args, **kwargs)
