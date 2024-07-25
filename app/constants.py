"""Constants module."""

from decimal import Decimal
from enum import StrEnum, auto

D0 = Decimal(0)


class HyphenatedStrEnum(StrEnum):
    """Enum where members are also (and must be) strings."""

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:  # noqa: ARG004
        """Return the hyphenated lower-cased version of the member name."""
        return name.lower().replace("_", "-")


class EventStatus(HyphenatedStrEnum):
    """Queue Message Status."""

    COMPLETED = auto()
    FAILED = auto()


class ServiceType(HyphenatedStrEnum):
    """Service Type."""

    STORAGE = auto()
    SHORT_JOB = auto()
    LONG_JOB = auto()


class LongJobStatus(HyphenatedStrEnum):
    """Long Job Status."""

    STARTED = auto()
    RUNNING = auto()
    FINISHED = auto()


class AccountType(HyphenatedStrEnum):
    """Account Type."""

    SYS = auto()
    VLAB = auto()
    PROJ = auto()
    RSV = auto()


class TransactionType(HyphenatedStrEnum):
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
