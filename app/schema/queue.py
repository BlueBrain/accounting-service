"""Queue schema."""

from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field, validate_call

from app.constants import LongrunStatus, ServiceSubtype, ServiceType

# min and max just ensure that the timestamp contains a reasonable value expressed in milliseconds
MIN_TS = datetime(2024, 1, 1, tzinfo=UTC).timestamp() * 1000
MAX_TS = datetime(2100, 1, 1, tzinfo=UTC).timestamp() * 1000


@validate_call
def _convert_timestamp(value: Annotated[float, Field(gt=MIN_TS, lt=MAX_TS)]) -> datetime:
    """Convert the provided value in unix time in milliseconds to datetime with timezone."""
    return datetime.fromtimestamp(value / 1000, tz=UTC)


TimeStamp = Annotated[datetime, BeforeValidator(_convert_timestamp)]


class StorageEvent(BaseModel):
    """StorageEvent."""

    type: Literal[ServiceType.STORAGE]
    subtype: Literal[ServiceSubtype.STORAGE] = ServiceSubtype.STORAGE
    proj_id: UUID
    size: Annotated[int, Field(ge=0)]
    timestamp: TimeStamp


class OneshotEvent(BaseModel):
    """OneshotEvent."""

    type: Literal[ServiceType.ONESHOT]
    subtype: ServiceSubtype
    proj_id: UUID
    job_id: UUID
    count: Annotated[int, Field(ge=0)]
    timestamp: TimeStamp


class LongrunEvent(BaseModel):
    """LongrunEvent."""

    type: Literal[ServiceType.LONGRUN]
    subtype: ServiceSubtype
    proj_id: UUID
    job_id: UUID
    status: LongrunStatus
    instances: Annotated[int | None, Field(ge=0)] = None
    instance_type: str | None = None
    timestamp: TimeStamp
