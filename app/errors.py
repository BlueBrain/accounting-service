"""Api exceptions."""

import dataclasses
from enum import auto
from http import HTTPStatus

from app.enum import UpperStrEnum


class ApiErrorCode(UpperStrEnum):
    """API Error codes."""

    INVALID_REQUEST = auto()
    ENTITY_NOT_FOUND = auto()
    ENTITY_ALREADY_EXISTS = auto()


@dataclasses.dataclass(kw_only=True)
class ApiError(Exception):
    """API Error."""

    message: str
    error_code: ApiErrorCode
    http_status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    details: str | None = None

    def __repr__(self) -> str:
        """Return the repr of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code}, "
            f"http_status_code={self.http_status_code}, "
            f"details={self.details})"
        )


class EventError(Exception):
    """Raised when failing to process a message in the queue."""
