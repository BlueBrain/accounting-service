"""Short jobs consumer module."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import TransactionType
from app.db.models import Job
from app.errors import EventError
from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import ShortJobEvent
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository
from app.repositories.ledger import LedgerRepository


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
        proj_account = await account_repo.get_proj_account(
            proj_id=event.proj_id,
            for_update=True,
        )
        rsv_account = await account_repo.get_reservation_account(
            proj_id=event.proj_id,
            for_update=True,
        )
        vlab_id = proj_account.parent_id
        proj_id = proj_account.id

        job = await job_repo.get_job(job_id=event.job_id)
        if job is None:
            err = f"Job {event.job_id} doesn't exist and it cannot be updated"
            raise EventError(err)
        if job.finished_at is not None:
            err = f"Job {event.job_id} is finished and it cannot be updated"
            raise EventError(err)
        if any(
            (
                job.vlab_id != vlab_id,
                job.proj_id != proj_id,
                job.service_type != event.type,
                job.service_subtype != event.subtype,
                job.reserved_units != event.count,
            )
        ):
            err = f"Job {event.job_id} has incompatible attributes"
            raise EventError(err)

        result = await job_repo.update_job(
            job_id=event.job_id,
            vlab_id=vlab_id,
            proj_id=proj_id,
            started_at=func.coalesce(Job.started_at, event.timestamp),
            last_alive_at=func.greatest(Job.last_alive_at, event.timestamp),
        )
        price = Decimal(event.count * 10)  # placeholder

        # TODO: use proj_account if the reservation account doesn't have enough funds
        await ledger_repo.insert_transaction(
            amount=price,
            debited_from=rsv_account.id,
            credited_to=system_account.id,
            transaction_datetime=event.timestamp,
            transaction_type=TransactionType.CHARGE_SHORT_JOBS,
            job_id=result.id,
        )
        return result.id
