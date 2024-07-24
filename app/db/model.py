"""DB Models."""

from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Identity, Index, SmallInteger, text, true
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
    message_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    queue_name: Mapped[str]
    status: Mapped[EventStatus]
    attributes: Mapped[dict[str, Any]]
    body: Mapped[str | None]
    error: Mapped[str | None]
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey("job.id"))
    counter: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]


class Job(Base):
    """Job table."""

    __tablename__ = "job"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    vlab_id: Mapped[UUID] = mapped_column(index=True)
    proj_id: Mapped[UUID] = mapped_column(index=True)
    service_type: Mapped[ServiceType]
    service_subtype: Mapped[str | None]
    usage_value: Mapped[BIGINT] = mapped_column(server_default=text("0"))
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]
    reserved_at: Mapped[datetime | None]
    started_at: Mapped[datetime | None]
    last_alive_at: Mapped[datetime | None]
    last_charged_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]
    cancelled_at: Mapped[datetime | None]
    properties: Mapped[dict[str, Any] | None]


class Account(Base):
    """Account table."""

    __tablename__ = "account"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    account_type: Mapped[AccountType]
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("account.id"))
    name: Mapped[str]
    balance: Mapped[Decimal] = mapped_column(server_default=text("0"))
    enabled: Mapped[bool] = mapped_column(server_default=true())
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]


class Journal(Base):
    """Journal table."""

    __tablename__ = "journal"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    transaction_datetime: Mapped[datetime]
    transaction_type: Mapped[TransactionType]
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey("job.id"))
    properties: Mapped[dict[str, Any] | None]
    created_at: Mapped[CREATED_AT]


class Ledger(Base):
    """Ledger table."""

    __tablename__ = "ledger"

    id: Mapped[BIGINT] = mapped_column(Identity(), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("account.id"))
    journal_id: Mapped[BIGINT] = mapped_column(ForeignKey("journal.id"))
    amount: Mapped[Decimal]
    created_at: Mapped[CREATED_AT]


Index(
    "only_one_system_account",
    Account.account_type,
    unique=True,
    postgresql_where=Account.account_type == AccountType.SYS,
)
