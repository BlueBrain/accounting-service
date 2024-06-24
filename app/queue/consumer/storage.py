import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.queue.consumer.base import QueueConsumer
from app.repositories.usage import UsageRepository


class StorageQueueConsumer(QueueConsumer):
    """Storage queue consumer."""

    async def consume(self, msg: dict[str, Any], db: AsyncSession) -> None:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        body = json.loads(msg["Body"])
        started_at = datetime.fromtimestamp(
            float(body.get("timestamp_ms") or msg["Attributes"]["SentTimestamp"]) / 1000,
            tz=UTC,
        )
        repo = UsageRepository(db=db)
        await repo.add_usage(
            vlab_id=UUID(body["vlab_id"]),
            proj_id=UUID(body["proj_id"]),
            job_id=None,
            service_type=body["type"],
            service_subtype=body.get("subtype", ""),
            units=int(body["units"]),
            started_at=started_at,
            finished_at=None,
            properties=None,
        )
