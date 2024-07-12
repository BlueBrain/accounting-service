"""Domain entities."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseAccount(BaseModel):
    """BaseAccount."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    balance: Decimal
    enabled: bool


class SysAccount(BaseAccount):
    """SysAccount."""


class VlabAccount(BaseAccount):
    """VlabAccount."""


class ProjAccount(BaseAccount):
    """ProjAccount."""

    vlab_id: Annotated[UUID, Field(alias="parent_id")]


class RsvAccount(BaseAccount):
    """RsvAccount."""

    proj_id: Annotated[UUID, Field(alias="parent_id")]


class Accounts(BaseModel):
    """Accounts."""

    vlab: VlabAccount
    proj: ProjAccount
    rsv: RsvAccount


@dataclass(kw_only=True)
class ChargeStorageResult:
    """Result of charge_storage."""

    not_charged: int = 0
    last_charged: int = 0
    new_ids: int = 0
    running_ids: int = 0
    transitioning_ids: int = 0


@dataclass(kw_only=True)
class ChargeLongJobsResult:
    """Result of charge_long_jobs."""

    unfinished_uncharged: int = 0
    unfinished_charged: int = 0
    finished_uncharged: int = 0
    finished_charged: int = 0
    finished_overcharged: int = 0
