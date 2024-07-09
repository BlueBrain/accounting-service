"""Short jobs consumer module."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import AccountType, TransactionType
from app.db.models import Job
from app.errors import EventError
from app.queue.consumer.base import QueueConsumer
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository
from app.repositories.ledger import LedgerRepository
from app.schemas.queue import ShortJobEvent


class ShortJobsQueueConsumer(QueueConsumer):
    """Short jobs queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = ShortJobEvent.model_validate_json(msg["Body"])
        job_repo = JobRepository(db=db)
        account_repo = AccountRepository(db=db)
        ledger_repo = LedgerRepository(db=db)

        system_account = await account_repo.get_system_account()
        accounts = await account_repo.get_accounts_by_proj_id(
            proj_id=event.proj_id, for_update={AccountType.PROJ, AccountType.RSV}
        )

        job = await job_repo.get_job(job_id=event.job_id)
        if job is None:
            err = f"Job {event.job_id} doesn't exist and it cannot be updated"
            raise EventError(err)
        if job.finished_at is not None:
            err = f"Job {event.job_id} is finished and it cannot be updated"
            raise EventError(err)
        if any(
            (
                job.vlab_id != accounts.vlab.id,
                job.proj_id != accounts.proj.id,
                job.service_type != event.type,
                job.service_subtype != event.subtype,
                job.reserved_units != event.count,
            )
        ):
            err = f"Job {event.job_id} has incompatible attributes"
            raise EventError(err)

        result = await job_repo.update_job(
            job_id=event.job_id,
            vlab_id=accounts.vlab.id,
            proj_id=accounts.proj.id,
            started_at=func.coalesce(Job.started_at, event.timestamp),
            last_alive_at=func.greatest(Job.last_alive_at, event.timestamp),
        )
        price = Decimal(event.count * 10)  # placeholder

        # TODO: use proj_account if the reservation account doesn't have enough funds
        await ledger_repo.insert_transaction(
            amount=price,
            debited_from=accounts.rsv.id,
            credited_to=system_account.id,
            transaction_datetime=event.timestamp,
            transaction_type=TransactionType.CHARGE_SHORT_JOBS,
            job_id=result.id,
        )
        return result.id
