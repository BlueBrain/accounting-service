"""Short jobs consumer module."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.queue.consumer.base import QueueConsumer
from app.queue.schemas import StorageEvent
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository
from app.utils import create_uuid


class StorageQueueConsumer(QueueConsumer):
    """Storage queue consumer."""

    async def _consume(self, msg: dict[str, Any], db: AsyncSession) -> UUID:
        """Consume the message."""
        self.logger.info("Message received: %s", msg)
        event = StorageEvent.model_validate_json(msg["Body"])

        job_repo = JobRepository(db=db)
        account_repo = AccountRepository(db=db)
        proj_account = await account_repo.get_proj_account(proj_id=event.proj_id)
        proj_id = proj_account.id
        vlab_id = proj_account.parent_id

        result = await job_repo.insert_job(
            job_id=create_uuid(),
            vlab_id=vlab_id,
            proj_id=proj_id,
            service_type=event.type,
            service_subtype=event.subtype,
            reserved_units=event.size,
            units=event.size,
            started_at=event.timestamp,
        )
        return result.id
