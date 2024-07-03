"""Ledger repository module."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa

from app.constants import TransactionType
from app.db.models import Account, Journal, Ledger
from app.logger import get_logger
from app.repositories.base import BaseRepository

L = get_logger(__name__)


class LedgerRepository(BaseRepository):
    """LedgerRepository."""

    async def insert_transaction(
        self,
        amount: Decimal,
        debited_from: UUID,
        credited_to: UUID,
        transaction_datetime: datetime,
        transaction_type: TransactionType,
        job_id: UUID | None,
        properties: dict | None = None,
    ) -> None:
        """Insert a transaction into journal and ledger, and update the balance accordingly."""
        query = (
            sa.insert(Journal)
            .values(
                transaction_datetime=transaction_datetime,
                transaction_type=transaction_type,
                job_id=job_id,
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
