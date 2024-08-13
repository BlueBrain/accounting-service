"""Generic utilities."""

import time
import uuid
from datetime import UTC, datetime


def since_unix_epoch() -> int:
    """Return the seconds since the Unix epoch."""
    return int(time.time())


def utcnow() -> datetime:
    """Return the current timestamp in UTC as a timezone-aware object."""
    return datetime.now(tz=UTC)


def create_uuid() -> uuid.UUID:
    """Return a new random UUID."""
    return uuid.uuid4()
