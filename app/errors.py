"""Api exceptions."""

import dataclasses
from collections.abc import Iterator
from contextlib import contextmanager
from enum import auto
from http import HTTPStatus

from sqlalchemy.exc import NoResultFound

from app.enum import UpperStrEnum


class ApiErrorCode(UpperStrEnum):
    """API Error codes."""

    INVALID_REQUEST = auto()
    ENTITY_NOT_FOUND = auto()
    ENTITY_ALREADY_EXISTS = auto()
    INSUFFICIENT_FUNDS = auto()


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


@contextmanager
def ensure_result(error_message: str) -> Iterator[None]:
    """Context manager that raises ApiError when no results are found after executing a query."""
    try:
        yield
    except NoResultFound as err:
        raise ApiError(
            message=error_message,
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
