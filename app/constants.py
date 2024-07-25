"""Constants module."""

from decimal import Decimal
from enum import auto

from app.enum import HyphenStrEnum

D0 = Decimal(0)


class EventStatus(HyphenStrEnum):
    """Queue Message Status."""

    COMPLETED = auto()
    FAILED = auto()


class ServiceType(HyphenStrEnum):
    """Service Type."""

    STORAGE = auto()
    SHORT_JOB = auto()
    LONG_JOB = auto()


class LongJobStatus(HyphenStrEnum):
    """Long Job Status."""

    STARTED = auto()
    RUNNING = auto()
    FINISHED = auto()


class AccountType(HyphenStrEnum):
    """Account Type."""

    SYS = auto()
    VLAB = auto()
    PROJ = auto()
    RSV = auto()


class TransactionType(HyphenStrEnum):
    """Transaction Type."""

    TOP_UP = auto()  # from SYS to VLAB
    ASSIGN_BUDGET = auto()  # from VLAB to PROJ
    REVERSE_BUDGET = auto()  # from PROJ to VLAB
    MOVE_BUDGET = auto()  # from PROJ to PROJ
    RESERVE = auto()  # from PROJ to RSV
    RELEASE = auto()  # from RSV to PROJ
    CHARGE_SHORT_JOB = auto()  # from RSV to SYS, or from PROJ to SYS
    CHARGE_LONG_JOB = auto()  # from RSV to SYS, or from PROJ to SYS
    CHARGE_STORAGE = auto()  # from RSV to SYS, or from PROJ to SYS
    REFUND = auto()  # from SYS to PROJ
