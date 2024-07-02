"""Short jobs consumer module."""

from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import TransactionType
from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import ShortJobUsageEvent
from app.repositories.account import AccountRepository
from app.repositories.ledger import LedgerRepository
from app.repositories.usage import UsageRepository


class ShortJobsQueueConsumer(QueueConsumer):
    """Short jobs queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> int:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = ShortJobUsageEvent.model_validate_json(msg["Body"])
        usage_repo = UsageRepository(db=db)
        account_repo = AccountRepository(db=db)
        ledger_repo = LedgerRepository(db=db)

        usage = await usage_repo.add_usage(
            vlab_id=event.vlab_id,
            proj_id=event.proj_id,
            job_id=event.job_id,
            service_type=event.type,
            service_subtype=event.subtype,
            units=event.count,
            started_at=event.timestamp,
            finished_at=event.timestamp,
        )
        amount = Decimal(event.count * 10)  # placeholder
        system_account = await account_repo.get_system_account()
        reservation_account = await account_repo.get_reservation_account(proj_id=event.proj_id)
        await ledger_repo.insert_transaction(
            amount=amount,
            debited_from=reservation_account.id,
            credited_to=system_account.id,
            transaction_datetime=event.timestamp,
            transaction_type=TransactionType.CHARGE_SHORT_JOBS,
            usage_id=usage.id,
        )
        return usage.id
