"""Api schema."""

from decimal import Decimal
from typing import Annotated, Any, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from app.constants import D0, ServiceSubtype, ServiceType
from app.errors import ApiErrorCode


class ApiResponse[T](BaseModel):
    """ApiResponse."""

    message: str
    data: T | None = None


class ErrorResponse(BaseModel, use_enum_values=True):
    """ErrorResponse."""

    error_code: ApiErrorCode
    message: str
    details: Any = None


class BaseReservationIn(BaseModel):
    """BaseReservationIn."""

    proj_id: UUID
    type: ServiceType
    subtype: ServiceSubtype


class OneshotReservationIn(BaseReservationIn):
    """OneshotReservationIn."""

    type: Literal[ServiceType.ONESHOT]
    count: Annotated[int, Field(ge=0)]


class LongrunReservationIn(BaseReservationIn):
    """LongrunReservationIn."""

    type: Literal[ServiceType.LONGRUN]
    duration: Annotated[int, Field(ge=0)]
    instances: Annotated[int, Field(ge=0)]
    instance_type: str | None = None


class ReservationOut(BaseModel):
    """ReservationOut."""

    job_id: UUID
    amount: Decimal


class SysAccountCreationIn(BaseModel):
    """SysAccountCreationIn."""

    id: UUID
    name: str


class VlabAccountCreationIn(BaseModel):
    """VlabAccountCreationIn."""

    id: UUID
    name: str


class ProjAccountCreationIn(BaseModel):
    """ProjAccountCreationIn."""

    id: UUID
    name: str
    vlab_id: UUID


class SysAccountCreationOut(BaseModel):
    """Returned when creating the system account."""

    id: UUID
    name: str


class VlabAccountCreationOut(BaseModel):
    """Returned when creating a new virtual lab."""

    id: UUID
    name: str


class ProjAccountCreationOut(BaseModel):
    """Returned when creating a new project."""

    id: UUID
    name: str


class TopUpIn(BaseModel):
    """TopUpIn."""

    vlab_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class AssignBudgetIn(BaseModel):
    """AssignBudgetIn."""

    vlab_id: UUID
    proj_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class ReverseBudgetIn(BaseModel):
    """ReverseBudgetIn."""

    vlab_id: UUID
    proj_id: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class MoveBudgetIn(BaseModel):
    """MoveBudgetIn."""

    vlab_id: UUID
    debited_from: UUID
    credited_to: UUID
    amount: Annotated[Decimal, Field(gt=D0)]


class AddPriceIn(BaseModel):
    """AddPriceIn."""

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


class AddPriceOut(AddPriceIn):
    """AddPriceOut."""

    id: int
