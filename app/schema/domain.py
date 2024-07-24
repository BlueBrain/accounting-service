"""Domain entities."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.constants import D0, ServiceType


class BaseAccount(BaseModel):
    """BaseAccount."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    balance: Decimal = D0
    enabled: bool = True


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


class BaseJob(BaseModel):
    """BaseJob."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    vlab_id: UUID
    proj_id: UUID
    service_type: ServiceType
    service_subtype: str | None
    usage_value: int
    reserved_at: datetime | None
    started_at: datetime | None
    last_alive_at: datetime | None
    last_charged_at: datetime | None
    finished_at: datetime | None
    properties: dict[str, Any] | None


class StartedJob(BaseJob):
    """StartedJob (finished or not)."""

    started_at: datetime
    last_alive_at: datetime


@dataclass(kw_only=True)
class ChargeLongJobResult:
    """Result of charge_long_job."""

    unfinished_uncharged: int = 0
    unfinished_charged: int = 0
    finished_uncharged: int = 0
    finished_charged: int = 0
    finished_overcharged: int = 0
    failure: int = 0


@dataclass(kw_only=True)
class ChargeShortJobResult:
    """Result of charge_short_job."""

    success: int = 0
    failure: int = 0


@dataclass(kw_only=True)
class ChargeStorageResult:
    """Result of charge_storage."""

    success: int = 0
    failure: int = 0
