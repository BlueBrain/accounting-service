"""Ledger repository module."""

from datetime import date
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa

from app.constants import TransactionType
from app.db.models import Journal, Ledger
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
        transaction_date: date,
        transaction_type: TransactionType,
        usage_id: int | None,
        properties: dict | None = None,
    ) -> None:
        """Insert a transaction into journal and ledger."""
        query = (
            sa.insert(Journal)
            .values(
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                usage_id=usage_id,
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
