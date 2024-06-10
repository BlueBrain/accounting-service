"""Models."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class."""


class Transactions(Base):
    """Transactions table."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal] = mapped_column()


class VlabTopup(Base):
    """VlabTopup table."""

    __tablename__ = "vlab_topup"

    id: Mapped[int] = mapped_column(primary_key=True)
    vlab_id: Mapped[uuid.UUID] = mapped_column(index=True)
    proj_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    stripe_event_id: Mapped[str] = mapped_column(String(30))
