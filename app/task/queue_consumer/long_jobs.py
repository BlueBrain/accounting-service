"""Long jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import LongJobStatus
from app.db.model import Job
from app.repository.group import RepositoryGroup
from app.schema.domain import Accounts
from app.schema.queue import LongJobEvent
from app.task.queue_consumer.base import QueueConsumer


async def _handle_started(repos: RepositoryGroup, event: LongJobEvent, accounts: Accounts) -> Job:
    return await repos.job.update_job(
        job_id=event.job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        started_at=event.timestamp,
        properties={"instance_type": event.instance_type},
    )


async def _handle_running(repos: RepositoryGroup, event: LongJobEvent, accounts: Accounts) -> Job:
    return await repos.job.update_job(
        job_id=event.job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        last_alive_at=event.timestamp,
    )


async def _handle_finished(repos: RepositoryGroup, event: LongJobEvent, accounts: Accounts) -> Job:
    return await repos.job.update_job(
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

        repos = RepositoryGroup(db=db)
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=event.proj_id)

        try:
            handler = {
                LongJobStatus.STARTED: _handle_started,
                LongJobStatus.RUNNING: _handle_running,
                LongJobStatus.FINISHED: _handle_finished,
            }[event.status]
        except KeyError:
            error = f"Status not handled: {event.status}"
            raise ValueError(error) from None

        result = await handler(repos, event=event, accounts=accounts)
        return result.id
