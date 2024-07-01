"""Queue message repository module."""

from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from app.constants import EventStatus
from app.db.models import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository):
    """EventRepository."""

    async def upsert(
        self,
        msg: dict[str, Any],
        queue_name: str,
        status: EventStatus,
        error: str | None = None,
        result_id: int | None = None,
    ) -> int | None:
        """Insert or update a record, and return a record counter >= 1."""
        query = insert(Event).values(
            message_id=msg["MessageId"],
            queue_name=queue_name,
            status=status,
            attributes=msg["Attributes"],
            body=msg["Body"],
            error=error,
            result_id=result_id,
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
                "result_id": result_id,
                "counter": Event.counter + 1,
                "updated_at": sa.func.now(),
            },
        ).returning(Event.counter)
        return (await self.db.execute(query)).scalar_one()
