"""Ledger repository module."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import func, true

from app.constants import D0, AccountType, TransactionType
from app.db.model import Account, Journal, Ledger
from app.logger import L
from app.repository.base import BaseRepository


class LedgerRepository(BaseRepository):
    """LedgerRepository."""

    async def insert_transaction(
        self,
        amount: Decimal,
        debited_from: UUID,
        credited_to: UUID,
        transaction_datetime: datetime,
        transaction_type: TransactionType,
        job_id: UUID | None = None,
        price_id: int | None = None,
        properties: dict | None = None,
    ) -> None:
        """Insert a transaction into journal and ledger, and update the balance accordingly."""
        if amount <= 0:
            L.warning("Negative transaction amount: {}", amount)
        query = (
            sa.insert(Journal)
            .values(
                transaction_datetime=transaction_datetime,
                transaction_type=transaction_type,
                job_id=job_id,
                price_id=price_id,
                properties=properties,
            )
            .returning(Journal.id)
        )
        journal_id = (await self.db.execute(query)).scalar_one()
        await self.db.execute(
            sa.insert(Ledger),
            [
                {
                    "account_id": debited_from,
                    "journal_id": journal_id,
                    "amount": -1 * amount,
                },
                {
                    "account_id": credited_to,
                    "journal_id": journal_id,
                    "amount": amount,
                },
            ],
        )
        (
            await self.db.execute(
                sa.update(Account)
                .values(balance=Account.balance + amount)
                .where(Account.id == credited_to)
                .returning(Account.balance)
            )
        ).one()
        (
            await self.db.execute(
                sa.update(Account)
                .values(balance=Account.balance - amount)
                .where(Account.id == debited_from)
                .returning(Account.balance)
            )
        ).one()

    async def get_remaining_reservation_for_job(
        self, *, job_id: UUID, account_id: UUID | None = None, raise_if_negative: bool = True
    ) -> Decimal:
        """Return the remaining reservation amount for a specific job."""
        query = (
            sa.select(
                func.sum(Ledger.amount).label("total"),
            )
            .select_from(Journal)
            .join(Ledger)
            .join(Account)
            .where(
                Journal.job_id == job_id,
                Account.account_type == AccountType.RSV,
                (Ledger.account_id == account_id) if account_id else true(),
            )
        )
        result = (await self.db.execute(query)).scalar_one() or D0
        if raise_if_negative and result < 0:
            err = f"Reservation for job {job_id} is negative: {result}"
            raise RuntimeError(err)
        return result
