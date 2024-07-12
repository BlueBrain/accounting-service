"""Job message repository module."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Row, null, or_, true
from sqlalchemy.dialects import postgresql as pg

from app.constants import ServiceType
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

    async def update_job(self, job_id: UUID, vlab_id: UUID, proj_id: UUID, **kwargs) -> Job:
        """Update an existing record."""
        query = (
            sa.update(Job)
            .values(**kwargs)
            .where(
                Job.id == job_id,
                Job.vlab_id == vlab_id,
                Job.proj_id == proj_id,
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

    async def get_storage_jobs_last_charged(
        self,
        *,
        project_ids: list[UUID] | None = None,
        min_charged_at: datetime | None = None,
    ) -> dict[UUID, Row]:
        """Get the job of type storage that was last charged, for each project."""
        query = (
            sa.select(Job.proj_id, Job.last_charged_at, Job.started_at, Job.id, Job.units)
            .distinct(Job.proj_id)
            .where(
                Job.service_type == ServiceType.STORAGE,
                Job.last_charged_at != null(),
                Job.started_at != null(),
                Job.proj_id.in_(project_ids) if project_ids is not None else true(),
                (Job.last_charged_at >= min_charged_at) if min_charged_at else true(),
            )
            .order_by(Job.proj_id, Job.last_charged_at.desc())
        )
        rows = (await self.db.execute(query)).all()
        return {row.proj_id: row for row in rows}

    async def get_storage_jobs_not_charged(
        self, *, project_ids: list[UUID] | None = None
    ) -> dict[UUID, Row]:
        """Get the job of type storage not charged yet, for each project.

        If there are multiple not-charged jobs per project, return the oldest one.
        """
        query = (
            sa.select(Job.proj_id, Job.started_at, Job.id, Job.units)
            .distinct(Job.proj_id)
            .where(
                Job.service_type == ServiceType.STORAGE,
                Job.last_charged_at == null(),
                Job.started_at != null(),
                Job.proj_id.in_(project_ids) if project_ids is not None else true(),
            )
            .order_by(Job.proj_id, Job.started_at)
        )
        rows = (await self.db.execute(query)).all()
        return {row.proj_id: row for row in rows}

    async def get_long_jobs_to_be_charged(
        self, *, project_ids: list[UUID] | None = None
    ) -> Sequence[Job]:
        """Get the long jobs to be charged.

        Return the jobs started having last_charged_at != finished_at,
        or where last_charged_at and/or finished_at are null.

        The records are NOT locked for update: if the consumer task updates the field `finished_at`
        during the transaction, the records will be selected again in the next round.
        """
        query = sa.select(Job).where(
            Job.service_type == ServiceType.LONG_JOBS,
            Job.started_at != null(),
            or_(
                Job.last_charged_at != Job.finished_at,
                Job.last_charged_at == null(),
                Job.finished_at == null(),
            ),
            Job.proj_id.in_(project_ids) if project_ids is not None else true(),
        )
        return (await self.db.execute(query)).scalars().all()
