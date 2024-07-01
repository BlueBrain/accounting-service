"""Constants module."""

from enum import StrEnum


class EventStatus(StrEnum):
    """Queue Message Status."""

    COMPLETED = "completed"
    FAILED = "failed"


class ServiceType(StrEnum):
    """Service Type."""

    STORAGE = "storage"
    SHORT_JOBS = "short-jobs"
    LONG_JOBS = "long-jobs"


class LongJobStatus(StrEnum):
    """Long Job Status."""

    STARTED = "started"
    RUNNING = "running"
    FINISHED = "finished"
