from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from app.constants import ServiceType
from app.db.models import Usage
from app.logger import get_logger
from app.repositories.base import BaseRepository

L = get_logger(__name__)


class UsageRepository(BaseRepository):
    """Usage Repository."""

    async def add_usage(
        self,
        vlab_id: UUID,
        proj_id: UUID,
        job_id: UUID | None,
        service_type: ServiceType,
        service_subtype: str | None,
        units: int,
        started_at: datetime,
        finished_at: datetime | None,
        properties: dict | None,
    ) -> None:
        """Add usage."""
        self.db.add(
            Usage(
                job_id=job_id,
                vlab_id=vlab_id,
                proj_id=proj_id,
                service_type=service_type,
                service_subtype=service_subtype,
                units=units,
                started_at=started_at,
                finished_at=finished_at,
                properties=properties,
            )
        )
        await self.db.commit()

    async def get_all_usages_rows(self) -> Sequence[sa.Row]:
        query = sa.select(Usage)
        res = await self.db.execute(query)
        return res.all()

    async def get_all_usages(self) -> Sequence[Usage]:
        query = sa.select(Usage)
        res = await self.db.scalars(query)
        return res.all()
