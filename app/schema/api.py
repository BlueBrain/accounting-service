"""Api schema."""

from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, model_validator

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

    job_id: UUID
    amount: Decimal


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


class AddPriceRequest(BaseModel):
    """AddPriceRequest."""

    service_type: ServiceType
    service_subtype: ServiceSubtype
    valid_from: AwareDatetime
    valid_to: AwareDatetime | None
    fixed_cost: Annotated[Decimal, Field(ge=D0)]
    multiplier: Annotated[Decimal, Field(ge=D0)]
    vlab_id: UUID | None

    @model_validator(mode="after")
    def check_validity_interval(self) -> Self:
        """Check that valid_to is greater than valid_from, if provided."""
        if self.valid_to is not None and self.valid_from >= self.valid_to:
            err = "valid_to must be greater than valid_from"
            raise ValueError(err)
        return self


class AddPriceResponse(AddPriceRequest):
    """AddPriceResponse."""

    id: int
