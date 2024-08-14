"""Common schema."""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer, validate_call

from app.config import settings
from app.utils import since_unix_epoch


@validate_call
def _convert_timestamp(value: int) -> datetime:
    """Convert value from seconds since the Unix epoch to datetime with timezone."""
    delta = int(value - since_unix_epoch())
    if not -settings.MAX_PAST_EVENT_TIMEDELTA < delta < settings.MAX_FUTURE_EVENT_TIMEDELTA:
        err = (
            f"Invalid timestamp {value}: it must be expressed in seconds since the Unix epoch, "
            f"and fall in the configured expected interval [detected delta={delta}]"
        )
        raise ValueError(err)
    return datetime.fromtimestamp(value, tz=UTC)


RecentTimeStamp = Annotated[
    datetime,
    BeforeValidator(_convert_timestamp),
    PlainSerializer(lambda x: int(x.timestamp())),
]
