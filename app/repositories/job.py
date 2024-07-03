"""Job message repository module."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_

from app.constants import ServiceType
from app.db.models import Job
from app.logger import get_logger
from app.repositories.base import BaseRepository

L = get_logger(__name__)


class JobRepository(BaseRepository):
    """JobRepository."""

    async def insert_job(  # noqa: PLR0913
        self,
        job_id: UUID,
        vlab_id: UUID,
        proj_id: UUID,
        service_type: ServiceType,
        service_subtype: str | None = None,
        units: int = 0,
        reserved_at: datetime | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        properties: dict | None = None,
    ) -> Job:
        """Insert a new job."""
        query = (
            sa.insert(Job)
            .values(
                id=job_id,
                vlab_id=vlab_id,
                proj_id=proj_id,
                service_type=service_type,
                service_subtype=service_subtype,
                units=units,
                reserved_at=reserved_at,
                started_at=started_at,
                last_alive_at=started_at,
                finished_at=finished_at,
                properties=properties,
            )
            .returning(Job)
        )
        return (await self.db.execute(query)).scalar_one()

    async def update_last_alive_at(
        self,
        vlab_id: UUID,
        proj_id: UUID,
        job_id: UUID,
        last_alive_at: datetime,
    ) -> Job:
        """Update last_alive_at."""
        query = (
            sa.update(Job)
            .values(
                last_alive_at=last_alive_at,
            )
            .where(
                and_(
                    Job.vlab_id == vlab_id,
                    Job.proj_id == proj_id,
                    Job.id == job_id,
                )
            )
            .returning(Job)
        )
        return (await self.db.execute(query)).scalar_one()

    async def update_finished_at(
        self,
        vlab_id: UUID,
        proj_id: UUID,
        job_id: UUID,
        finished_at: datetime,
    ) -> Job:
        """Update finished_at."""
        query = (
            sa.update(Job)
            .values(
                finished_at=finished_at,
            )
            .where(
                and_(
                    Job.vlab_id == vlab_id,
                    Job.proj_id == proj_id,
                    Job.id == job_id,
                )
            )
            .returning(Job)
        )
        return (await self.db.execute(query)).scalar_one()

    async def get_all_rows(self) -> Sequence[sa.Row]:
        """Get all the rows as Row objects."""
        query = sa.select(Job)
        res = await self.db.execute(query)
        return res.all()

    async def get_all(self) -> Sequence[Job]:
        """Get all the rows as Job objects."""
        query = sa.select(Job)
        res = await self.db.scalars(query)
        return res.all()
