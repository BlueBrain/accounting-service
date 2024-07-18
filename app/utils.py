"""Generic utilities."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar

T = TypeVar("T")


def utcnow() -> datetime:
    """Return the current timestamp in UTC as a timezone-aware object."""
    return datetime.now(tz=UTC)


def create_uuid() -> uuid.UUID:
    """Return a new random UUID."""
    return uuid.uuid4()


def one_or_none(seq: Sequence[T]) -> T | None:
    """Return the single item of the sequence, or None if the sequence is empty."""
    if len(seq) > 1:
        err = f"Too many items: {len(seq)}, expected 1 or 0"
        raise ValueError(err)
    return seq[0] if seq else None
