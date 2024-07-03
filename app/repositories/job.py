"""Job message repository module."""

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy.dialects import postgresql as pg

from app.db.models import Job
from app.logger import get_logger
from app.repositories.base import BaseRepository

L = get_logger(__name__)


class JobRepository(BaseRepository):
    """JobRepository."""

    async def get_job(self, job_id: UUID) -> Job | None:
        """Get an existing job by id, or return None if it doesn't exist."""
        query = sa.select(Job).where(Job.id == job_id)
        return (await self.db.execute(query)).scalar_one_or_none()

    async def insert_job(self, job_id: UUID, **kwargs) -> Job:
        """Insert a new job."""
        query = sa.insert(Job).values(id=job_id, **kwargs).returning(Job)
        return (await self.db.execute(query)).scalar_one()

    async def upsert_job(self, job_id: UUID, *, query_update_fields: list[str], **kwargs) -> Job:
        """Insert or update a job."""
        update_values = {key: kwargs[key] for key in query_update_fields}
        query = (
            pg.insert(Job)
            .values(id=job_id, **kwargs)
            .on_conflict_do_update(index_elements=["id"], set_=update_values)
            .returning(Job)
        )
        return (await self.db.execute(query)).scalar_one()

    async def update_job(self, job_id: UUID, vlab_id: UUID | None, proj_id: UUID, **kwargs) -> Job:
        """Update an existing record."""
        query = (
            sa.update(Job)
            .values(id=job_id, **kwargs)
            .where(
                and_(
                    Job.id == job_id,
                    Job.vlab_id == vlab_id,
                    Job.proj_id == proj_id,
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
