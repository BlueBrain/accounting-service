"""DB Models."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar

from sqlalchemy import DateTime, ForeignKey, Identity, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.constants import AccountType, EventStatus, ServiceType, TransactionType
from app.db.types import BIGINT, CREATED_AT, UPDATED_AT


class Base(DeclarativeBase):
    """Base class."""

    type_annotation_map: ClassVar[dict] = {
        datetime: DateTime(timezone=True),
        dict[str, Any]: JSONB,
    }


class Event(Base):
    """Queue events table."""

    __tablename__ = "event"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    message_id: Mapped[uuid.UUID] = mapped_column(index=True, unique=True)
    queue_name: Mapped[str]
    status: Mapped[EventStatus]
    attributes: Mapped[dict[str, Any]]
    body: Mapped[str | None]
    error: Mapped[str | None]
    result_id: Mapped[int | None]
    counter: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]


class Usage(Base):
    """Usage table."""

    __tablename__ = "usage"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    job_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    service_type: Mapped[ServiceType]
    service_subtype: Mapped[str | None]
    units: Mapped[BIGINT]
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]
    started_at: Mapped[datetime]
    last_alive_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    properties: Mapped[dict[str, Any] | None]


class Account(Base):
    """Account table."""

    __tablename__ = "account"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    account_type: Mapped[AccountType]
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("account.id"))
    name: Mapped[str]
    enabled: Mapped[bool]
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]


class Journal(Base):
    """Journal table."""

    __tablename__ = "journal"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    transaction_date: Mapped[date]
    transaction_type: Mapped[TransactionType]
    usage_id: Mapped[BIGINT | None] = mapped_column(ForeignKey("usage.id"))
    properties: Mapped[dict[str, Any] | None]
    created_at: Mapped[CREATED_AT]


class Ledger(Base):
    """Ledger table."""

    __tablename__ = "ledger"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.id"))
    journal_id: Mapped[BIGINT] = mapped_column(ForeignKey("journal.id"))
    amount: Mapped[Decimal]
    created_at: Mapped[CREATED_AT]
