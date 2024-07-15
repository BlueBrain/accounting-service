"""Long jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import LongJobStatus
from app.db.models import Job
from app.queue.consumer.base import QueueConsumer
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository
from app.schemas.domain import Accounts
from app.schemas.queue import LongJobEvent


async def _handle_started(job_repo: JobRepository, event: LongJobEvent, accounts: Accounts) -> Job:
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        started_at=event.timestamp,
        properties={"instance_type": event.instance_type},
    )


async def _handle_running(job_repo: JobRepository, event: LongJobEvent, accounts: Accounts) -> Job:
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        last_alive_at=event.timestamp,
    )


async def _handle_finished(job_repo: JobRepository, event: LongJobEvent, accounts: Accounts) -> Job:
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        finished_at=event.timestamp,
    )


class LongJobsQueueConsumer(QueueConsumer):
    """Long jobs queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = LongJobEvent.model_validate_json(msg["Body"])

        job_repo = JobRepository(db=db)
        account_repo = AccountRepository(db=db)
        accounts = await account_repo.get_accounts_by_proj_id(proj_id=event.proj_id)

        try:
            handler = {
                LongJobStatus.STARTED: _handle_started,
                LongJobStatus.RUNNING: _handle_running,
                LongJobStatus.FINISHED: _handle_finished,
            }[event.status]
        except KeyError:
            error = f"Status not handled: {event.status}"
            raise ValueError(error) from None

        result = await handler(job_repo, event=event, accounts=accounts)
        return result.id
