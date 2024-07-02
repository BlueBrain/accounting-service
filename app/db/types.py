"""DB types."""

from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import mapped_column

BIGINT = Annotated[int, mapped_column(BigInteger)]

CREATED_AT = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), index=True),
]

UPDATED_AT = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]
