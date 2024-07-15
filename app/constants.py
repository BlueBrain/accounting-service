"""Constants module."""

from decimal import Decimal
from enum import StrEnum, auto

D0 = Decimal(0)


class EventStatus(StrEnum):
    """Queue Message Status."""

    COMPLETED = auto()
    FAILED = auto()


class ServiceType(StrEnum):
    """Service Type."""

    STORAGE = auto()
    SHORT_JOBS = auto()
    LONG_JOBS = auto()


class LongJobStatus(StrEnum):
    """Long Job Status."""

    STARTED = auto()
    RUNNING = auto()
    FINISHED = auto()


class AccountType(StrEnum):
    """Account Type."""

    SYS = auto()
    VLAB = auto()
    PROJ = auto()
    RSV = auto()


class TransactionType(StrEnum):
    """Transaction Type."""

    TOPUP = auto()  # from SYS to VLAB
    ASSIGN = auto()  # from VLAB to PROJ, or from PROJ to VLAB
    RESERVE = auto()  # from PROJ to RSV
    RELEASE = auto()  # from RSV to PROJ
    CHARGE_SHORT_JOBS = auto()  # from RSV to SYS, or from PROJ to SYS
    CHARGE_LONG_JOBS = auto()  # from RSV to SYS, or from PROJ to SYS
    CHARGE_STORAGE = auto()  # from RSV to SYS, or from PROJ to SYS
    REFUND = auto()  # from SYS to PROJ
