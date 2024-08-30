"""Api schema."""

from decimal import Decimal
from typing import Annotated, Any, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, model_validator

from app.constants import D0, ServiceSubtype, ServiceType
from app.errors import ApiErrorCode
from app.schema.common import BaseModel, FormattedDecimal


class ApiResponse[T](BaseModel):
    """ApiResponse."""

    message: str
    data: T | None = None


class ErrorResponse(BaseModel, use_enum_values=True):
    """ErrorResponse."""

    error_code: ApiErrorCode
    message: str
    details: Any = None


class BaseMakeReservationIn(BaseModel):
    """BaseMakeReservationIn."""

    proj_id: UUID
    type: ServiceType
    subtype: ServiceSubtype


class MakeOneshotReservationIn(BaseMakeReservationIn):
    """MakeOneshotReservationIn."""

    type: Literal[ServiceType.ONESHOT]
    count: Annotated[int, Field(ge=0)]


class MakeLongrunReservationIn(BaseMakeReservationIn):
    """MakeLongrunReservationIn."""

    type: Literal[ServiceType.LONGRUN]
    duration: Annotated[int, Field(ge=0)]
    instances: Annotated[int, Field(ge=0)]
    instance_type: str | None = None


class MakeReservationOut(BaseModel):
    """MakeReservationOut."""

    job_id: UUID
    amount: Decimal


class ReleaseReservationOut(BaseModel):
    """ReleaseReservationOut."""

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


class ProjBalanceOut(BaseModel):
    """ProjBalanceOut."""

    proj_id: UUID
    balance: FormattedDecimal
    reservation: FormattedDecimal


class VlabBalanceOut(BaseModel):
    """VlabBalanceOut."""

    vlab_id: UUID
    balance: FormattedDecimal
    projects: list[ProjBalanceOut] | None = None


class SysBalanceOut(BaseModel):
    """SysBalanceOut."""

    balance: FormattedDecimal


class OneshotReportOut(BaseModel, from_attributes=True):
    """OneshotReportOut."""

    job_id: UUID
    type: Literal[ServiceType.ONESHOT]
    subtype: ServiceSubtype
    reserved_at: AwareDatetime
    started_at: AwareDatetime
    amount: Decimal
    count: Annotated[int, Field(ge=0)]
    reserved_amount: Decimal
    reserved_count: Annotated[int, Field(ge=0)]


class LongrunReportOut(BaseModel, from_attributes=True):
    """LongrunReportOut."""

    job_id: UUID
    type: Literal[ServiceType.LONGRUN]
    subtype: ServiceSubtype
    reserved_at: AwareDatetime
    started_at: AwareDatetime
    finished_at: AwareDatetime
    cancelled_at: AwareDatetime
    amount: Decimal
    duration: Annotated[int, Field(ge=0)]
    reserved_amount: Decimal
    reserved_duration: Annotated[int, Field(ge=0)]


class StorageReportOut(BaseModel, from_attributes=True):
    """StorageReportOut."""

    job_id: UUID
    type: Literal[ServiceType.STORAGE]
    subtype: ServiceSubtype
    started_at: AwareDatetime
    finished_at: AwareDatetime
    amount: Decimal
    duration: Annotated[int, Field(ge=0)]
    size: Annotated[int, Field(ge=0)]


JobReportUnionOut = Annotated[
    OneshotReportOut | LongrunReportOut | StorageReportOut,
    Field(discriminator="type"),
]


class ProjReportOut(BaseModel):
    """ProjReportOut."""

    proj_id: UUID
    jobs: list[JobReportUnionOut]


class VlabReportOut(BaseModel):
    """VlabReportOut."""

    vlab_id: UUID
    projects: list[ProjReportOut]
