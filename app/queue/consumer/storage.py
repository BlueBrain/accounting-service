"""Short jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import StorageEvent
from app.repositories.job import JobRepository
from app.utils import create_uuid


class StorageQueueConsumer(QueueConsumer):
    """Storage queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = StorageEvent.model_validate_json(msg["Body"])
        repo = JobRepository(db=db)
        result = await repo.insert_job(
            job_id=event.job_id or create_uuid(),
            vlab_id=event.vlab_id,
            proj_id=event.proj_id,
            service_type=event.type,
            service_subtype=event.subtype,
            units=event.size,
            started_at=event.timestamp,
        )
        return result.id
