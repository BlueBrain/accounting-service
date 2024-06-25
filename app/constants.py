"""Constants module."""

from enum import StrEnum


class ServiceType(StrEnum):
    """Service type."""

    STORAGE = "storage"
    SHORT_JOBS = "short-jobs"
    LONG_JOBS = "long-jobs"


class QueueMessageStatus(StrEnum):
    """Queue message status."""

    COMPLETED = "completed"
    FAILED = "failed"
