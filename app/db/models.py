"""Models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, ClassVar

from sqlalchemy import BigInteger, DateTime, Identity, SmallInteger, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.constants import QueueMessageStatus, ServiceType

CREATED_AT = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), index=True),
]
UPDATED_AT = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]


class Base(DeclarativeBase):
    """Base class."""

    type_annotation_map: ClassVar[dict] = {
        datetime: DateTime(timezone=True),
        dict[str, Any]: JSONB,
    }


class QueueMessage(Base):
    """Queue messages table."""

    __tablename__ = "queue_message"

    message_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    queue_name: Mapped[str]
    status: Mapped[QueueMessageStatus]
    attributes: Mapped[dict[str, Any]]
    body: Mapped[str | None]
    error: Mapped[str | None]
    counter: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]


class Usage(Base):
    """Usage table."""

    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    job_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    service_type: Mapped[ServiceType]
    service_subtype: Mapped[str | None]
    units: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]
    started_at: Mapped[datetime]
    last_alive_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    properties: Mapped[dict[str, Any] | None]


class Transactions(Base):
    """Transactions table."""

    # wip

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal]


class VlabTopup(Base):
    """VlabTopup table."""

    # wip

    __tablename__ = "vlab_topup"

    id: Mapped[int] = mapped_column(primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal]
    created_at: Mapped[CREATED_AT]
    stripe_event_id: Mapped[str]
