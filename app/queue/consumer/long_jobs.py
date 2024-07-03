"""Long jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import LongJobStatus
from app.db.models import Job
from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import LongJobEvent
from app.repositories.job import JobRepository


async def _handle_started(repo: JobRepository, event: LongJobEvent) -> Job:
    return await repo.insert_job(
        vlab_id=event.vlab_id,
        proj_id=event.proj_id,
        job_id=event.job_id,
        service_type=event.type,
        service_subtype=event.subtype,
        units=event.instances or 0,
        started_at=event.timestamp,
        properties={"instance_type": event.instance_type},
    )


async def _handle_running(repo: JobRepository, event: LongJobEvent) -> Job:
    return await repo.update_last_alive_at(
        vlab_id=event.vlab_id,
        proj_id=event.proj_id,
        job_id=event.job_id,
        last_alive_at=event.timestamp,
    )


async def _handle_finished(repo: JobRepository, event: LongJobEvent) -> Job:
    return await repo.update_finished_at(
        vlab_id=event.vlab_id,
        proj_id=event.proj_id,
        job_id=event.job_id,
        finished_at=event.timestamp,
    )


class LongJobsQueueConsumer(QueueConsumer):
    """Long jobs queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = LongJobEvent.model_validate_json(msg["Body"])
        repo = JobRepository(db=db)
        match event.status:
            case LongJobStatus.STARTED:
                result = await _handle_started(repo, event)
            case LongJobStatus.RUNNING:
                result = await _handle_running(repo, event)
            case LongJobStatus.FINISHED:
                result = await _handle_finished(repo, event)
            case _:
                error = f"Status not handled: {event.status}"
                raise ValueError(error)
        return result.id
