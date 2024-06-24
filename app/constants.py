from enum import StrEnum


class ServiceType(StrEnum):
    STORAGE = "storage"
    SHORT_JOBS = "short-jobs"
    LONG_JOBS = "long-jobs"


class QueueMessageStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
