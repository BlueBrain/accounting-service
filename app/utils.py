"""Generic utilities."""

import uuid
from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return the current timestamp in UTC as a timezone-aware object."""
    return datetime.now(tz=UTC)


def create_uuid() -> uuid.UUID:
    """Return a new random UUID."""
    return uuid.uuid4()
