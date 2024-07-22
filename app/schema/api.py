"""Api schema."""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.constants import ServiceType


class ReservationRequest(BaseModel):
    """ReservationRequest."""

    proj_id: UUID
    type: ServiceType
    subtype: str | None = None


class ShortJobsReservationRequest(ReservationRequest):
    """ShortJobsReservationRequest."""

    type: Literal[ServiceType.SHORT_JOBS]
    count: int


class LongJobsReservationRequest(ReservationRequest):
    """LongJobsReservationRequest."""

    type: Literal[ServiceType.LONG_JOBS]
    instances: int = 1
    instance_type: str | None = None


class ReservationResponse(BaseModel):
    """ReservationResponse."""

    is_allowed: bool
    requested_amount: Decimal
    available_amount: Decimal
    job_id: UUID | None = None


class SysAccountCreationRequest(BaseModel):
    """SysAccountCreationRequest."""

    id: UUID
    name: str


class VlabAccountCreationRequest(BaseModel):
    """VlabAccountCreationRequest."""

    id: UUID
    name: str


class ProjAccountCreationRequest(BaseModel):
    """ProjAccountCreationRequest."""

    id: UUID
    name: str
    vlab_id: UUID


class SysAccountCreationResponse(BaseModel):
    """Response returned when creating the system account."""

    id: UUID
    name: str


class VlabAccountCreationResponse(BaseModel):
    """Response returned when creating a new virtual lab."""

    id: UUID
    name: str


class ProjAccountCreationResponse(BaseModel):
    """Response returned when creating a new project."""

    id: UUID
    name: str
