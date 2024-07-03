"""Queue schemas."""

from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field, validate_call

from app.constants import LongJobStatus, ServiceType

# min and max just ensure that the timestamp contains a reasonable value expressed in milliseconds
MIN_TS = datetime(2024, 1, 1, tzinfo=UTC).timestamp() * 1000
MAX_TS = datetime(2100, 1, 1, tzinfo=UTC).timestamp() * 1000


@validate_call
def _convert_timestamp(value: Annotated[float, Field(gt=MIN_TS, lt=MAX_TS)]) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=UTC)


TimeStamp = Annotated[datetime, BeforeValidator(_convert_timestamp)]


class StorageEvent(BaseModel):
    """StorageEvent."""

    type: Literal[ServiceType.STORAGE]
    subtype: str | None = None
    proj_id: UUID
    size: int
    timestamp: TimeStamp


class ShortJobEvent(BaseModel):
    """ShortJobEvent."""

    type: Literal[ServiceType.SHORT_JOBS]
    subtype: str
    proj_id: UUID
    job_id: UUID
    count: int
    timestamp: TimeStamp


class LongJobEvent(BaseModel):
    """LongJobEvent."""

    type: Literal[ServiceType.LONG_JOBS]
    subtype: str
    proj_id: UUID
    job_id: UUID
    status: LongJobStatus
    instances: int | None = None
    instance_type: str | None = None
    timestamp: TimeStamp
