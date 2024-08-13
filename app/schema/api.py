"""Api schema."""

from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants import D0, ServiceSubtype, ServiceType
from app.errors import ApiErrorCode


class ErrorResponse(BaseModel):
    """ErrorResponse."""

    error_code: ApiErrorCode
    message: str
    details: str | None = None


class BaseReservationRequest(BaseModel):
    """BaseReservationRequest."""

    proj_id: UUID
    type: ServiceType
    subtype: ServiceSubtype


class OneshotReservationRequest(BaseReservationRequest):
    """OneshotReservationRequest."""

    type: Literal[ServiceType.ONESHOT]
    count: Annotated[int, Field(ge=0)]


class LongrunReservationRequest(BaseReservationRequest):
    """LongrunReservationRequest."""

    type: Literal[ServiceType.LONGRUN]
    duration: Annotated[int, Field(ge=0)]
    instances: Annotated[int, Field(ge=0)]
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


class TopUpRequest(BaseModel):
    """TopUpRequest."""

    vlab_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class AssignBudgetRequest(BaseModel):
    """AssignBudgetRequest."""

    vlab_id: UUID
    proj_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class ReverseBudgetRequest(BaseModel):
    """ReverseBudgetRequest."""

    vlab_id: UUID
    proj_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class MoveBudgetRequest(BaseModel):
    """MoveBudgetRequest."""

    vlab_id: UUID
    debited_from: UUID
    credited_to: UUID
    amount: Annotated[Decimal, Field(gt=D0)]
