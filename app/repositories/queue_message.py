"""Queue message repository module."""

from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from app.constants import QueueMessageStatus
from app.db.models import QueueMessage
from app.repositories.base import BaseRepository


class QueueMessageRepository(BaseRepository):
    """QueueMessageRepository."""

    async def upsert(
        self,
        msg: dict[str, Any],
        queue_name: str,
        status: QueueMessageStatus,
        error: str | None = None,
    ) -> int:
        """Insert or update a record, and return a record counter >= 1."""
        query = insert(QueueMessage).values(
            message_id=msg["MessageId"],
            queue_name=queue_name,
            status=status,
            attributes=msg["Attributes"],
            body=msg["Body"],
            error=error,
            counter=1,
        )
        query = query.on_conflict_do_update(
            index_elements=["message_id"],
            set_={
                "queue_name": queue_name,
                "status": status,
                "attributes": msg["Attributes"],
                "body": msg["Body"],
                "error": error,
                "counter": QueueMessage.counter + 1,
                "updated_at": sa.func.now(),
            },
        ).returning(QueueMessage.counter)
        res = await self.db.execute(query)
        await self.db.commit()
        return res.scalar()
