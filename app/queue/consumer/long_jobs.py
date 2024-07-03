"""Long jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import LongJobStatus
from app.db.models import Job
from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import LongJobEvent
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository


async def _handle_started(
    job_repo: JobRepository, event: LongJobEvent, vlab_id: UUID | None, proj_id: UUID
) -> Job:
    units = (event.instances or 1) * 10  # TODO: calculate the correct units
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=vlab_id,
        proj_id=proj_id,
        units=units,
        started_at=event.timestamp,
        properties={"instance_type": event.instance_type},
    )


async def _handle_running(
    job_repo: JobRepository, event: LongJobEvent, vlab_id: UUID | None, proj_id: UUID
) -> Job:
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=vlab_id,
        proj_id=proj_id,
        last_alive_at=event.timestamp,
    )


async def _handle_finished(
    job_repo: JobRepository, event: LongJobEvent, vlab_id: UUID | None, proj_id: UUID
) -> Job:
    return await job_repo.update_job(
        job_id=event.job_id,
        vlab_id=vlab_id,
        proj_id=proj_id,
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
        proj_account = await account_repo.get_proj_account(proj_id=event.proj_id)
        proj_id = proj_account.id
        vlab_id = proj_account.parent_id

        match event.status:
            case LongJobStatus.STARTED:
                result = await _handle_started(job_repo, event, vlab_id=vlab_id, proj_id=proj_id)
            case LongJobStatus.RUNNING:
                result = await _handle_running(job_repo, event, vlab_id=vlab_id, proj_id=proj_id)
            case LongJobStatus.FINISHED:
                result = await _handle_finished(job_repo, event, vlab_id=vlab_id, proj_id=proj_id)
            case _:
                error = f"Status not handled: {event.status}"
                raise ValueError(error)
        return result.id
