"""Short jobs consumer module."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import StorageUsageEvent
from app.repositories.usage import UsageRepository


class StorageQueueConsumer(QueueConsumer):
    """Storage queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> int:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = StorageUsageEvent.model_validate_json(msg["Body"])
        repo = UsageRepository(db=db)
        usage = await repo.add_usage(
            vlab_id=event.vlab_id,
            proj_id=event.proj_id,
            job_id=event.job_id,
            service_type=event.type,
            service_subtype=event.subtype,
            units=event.size,
            started_at=event.timestamp,
        )
        return usage.id
