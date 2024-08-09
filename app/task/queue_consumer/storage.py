"""Storage consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.group import RepositoryGroup
from app.schema.queue import StorageEvent
from app.task.queue_consumer.base import QueueConsumer
from app.utils import create_uuid


class StorageQueueConsumer(QueueConsumer):
    """Storage queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: {}", msg)
        event = StorageEvent.model_validate_json(msg["Body"])

        repos = RepositoryGroup(db=db)
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=event.proj_id)

        # close the old running job(s)
        await repos.job.update_finished_at(
            vlab_id=accounts.vlab.id,
            proj_id=accounts.proj.id,
            service_type=event.type,
            finished_at=event.timestamp,
        )
        # insert a new job
        result = await repos.job.insert_job(
            job_id=create_uuid(),
            vlab_id=accounts.vlab.id,
            proj_id=accounts.proj.id,
            service_type=event.type,
            service_subtype=event.subtype,
            started_at=event.timestamp,
            last_alive_at=event.timestamp,
            usage_params={
                "size": event.size,
            },
        )
        return result.id
