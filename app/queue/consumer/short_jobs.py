from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.queue.consumer.base import QueueConsumer


class ShortJobsQueueConsumer(QueueConsumer):
    """Short jobs queue consumer."""

    async def consume(self, msg: dict[str, Any], db: AsyncSession) -> None:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
