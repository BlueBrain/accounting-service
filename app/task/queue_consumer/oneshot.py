"""Oneshot job consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import AccountType
from app.errors import EventError
from app.repository.group import RepositoryGroup
from app.schema.queue import OneshotEvent
from app.task.queue_consumer.base import QueueConsumer


class OneshotQueueConsumer(QueueConsumer):
    """Oneshot queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: {}", msg)
        event = OneshotEvent.model_validate_json(msg["Body"])
        repos = RepositoryGroup(db=db)

        accounts = await repos.account.get_accounts_by_proj_id(
            proj_id=event.proj_id, for_update={AccountType.PROJ, AccountType.RSV}
        )

        job = await repos.job.get_job(job_id=event.job_id)
        if job is None:
            err = f"Job {event.job_id} doesn't exist and it cannot be updated"
            raise EventError(err)
        if job.finished_at is not None:
            err = f"Job {event.job_id} is finished and it cannot be updated"
            raise EventError(err)
        if unmatched_attributes := {
            key: value
            for key, value in [
                ("vlab_id", job.vlab_id == accounts.vlab.id),
                ("proj_id", job.proj_id == accounts.proj.id),
                ("service_type", job.service_type == event.type),
                ("service_subtype", job.service_subtype == event.subtype),
                ("usage_value", job.usage_value == event.count),
            ]
            if not value
        }:
            err = f"Job {event.job_id} has incompatible attributes: {sorted(unmatched_attributes)}"
            raise EventError(err)

        result = await repos.job.update_job(
            job_id=event.job_id,
            vlab_id=accounts.vlab.id,
            proj_id=accounts.proj.id,
            started_at=event.timestamp,
            last_alive_at=event.timestamp,
            finished_at=event.timestamp,
            usage_value=event.count,
        )
        return result.id
