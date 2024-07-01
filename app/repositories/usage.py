"""Usage message repository module."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_

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
        service_subtype: str | None = None,
        units: int = 0,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        properties: dict | None = None,
    ) -> Usage:
        """Add usage."""
        query = (
            sa.insert(Usage)
            .values(
                vlab_id=vlab_id,
                proj_id=proj_id,
                job_id=job_id,
                service_type=service_type,
                service_subtype=service_subtype,
                units=units,
                started_at=started_at,
                last_alive_at=started_at,
                finished_at=finished_at,
                properties=properties,
            )
            .returning(Usage)
        )
        return (await self.db.execute(query)).scalar_one()

    async def update_last_alive_at(
        self,
        vlab_id: UUID,
        proj_id: UUID,
        job_id: UUID,
        last_alive_at: datetime,
    ) -> Usage:
        """Update last_alive_at."""
        query = (
            sa.update(Usage)
            .values(
                last_alive_at=last_alive_at,
            )
            .where(
                and_(
                    Usage.vlab_id == vlab_id,
                    Usage.proj_id == proj_id,
                    Usage.job_id == job_id,
                )
            )
            .returning(Usage)
        )
        return (await self.db.execute(query)).scalar_one()

    async def update_finished_at(
        self,
        vlab_id: UUID,
        proj_id: UUID,
        job_id: UUID,
        finished_at: datetime,
    ) -> Usage:
        """Update finished_at."""
        query = (
            sa.update(Usage)
            .values(
                finished_at=finished_at,
            )
            .where(
                and_(
                    Usage.vlab_id == vlab_id,
                    Usage.proj_id == proj_id,
                    Usage.job_id == job_id,
                )
            )
            .returning(Usage)
        )
        return (await self.db.execute(query)).scalar_one()

    async def get_all_usages_rows(self) -> Sequence[sa.Row]:
        """Get all the usage rows as Row objects."""
        query = sa.select(Usage)
        res = await self.db.execute(query)
        return res.all()

    async def get_all_usages(self) -> Sequence[Usage]:
        """Get all the usage rows as Usage objects."""
        query = sa.select(Usage)
        res = await self.db.scalars(query)
        return res.all()
