"""Job report repository module."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Integer, Row, and_, case, func, true

from app.constants import D0, TransactionType
from app.db.model import Job, Journal, Ledger
from app.repository.base import BaseRepository
from app.schema.api import PaginatedParams


class ReportRepository(BaseRepository):
    """ReportRepository."""

    async def get_job_reports(
        self,
        pagination: PaginatedParams,
        vlab_id: UUID | None = None,
        proj_id: UUID | None = None,
        started_after: datetime | None = None,
        started_before: datetime | None = None,
    ) -> tuple[Sequence[Row], int]:
        """Return a page of job reports for a given project, and the total number of jobs."""
        order_by_columns = (Job.started_at, Job.id)
        base_query = (
            sa.select(Job.id)
            .select_from(Job)
            .where(
                Job.finished_at == Job.last_charged_at,
                (Job.vlab_id == vlab_id) if vlab_id else true(),
                (Job.proj_id == proj_id) if proj_id else true(),
                (Job.started_at >= started_after) if started_after else true(),
                (Job.started_at < started_before) if started_before else true(),
            )
        )
        count_query = base_query.with_only_columns(func.count())
        count = (await self.db.execute(count_query)).scalar_one()
        selected_job_query = (
            base_query.order_by(*order_by_columns)
            .limit(pagination.page_size)
            .offset(pagination.page_size * (pagination.page - 1))
            .subquery("selected_job")
        )
        query = (
            sa.select(
                *([Job.vlab_id] if vlab_id is None and proj_id is None else []),
                *([Job.proj_id] if proj_id is None else []),
                Job.id.label("job_id"),
                Job.service_type.label("type"),
                Job.service_subtype.label("subtype"),
                Job.reserved_at,
                Job.started_at,
                Job.finished_at,
                Job.cancelled_at,
                (func.coalesce(-func.sum(Ledger.amount), D0)).label("amount"),
                (
                    -func.sum(
                        case(
                            (
                                Journal.transaction_type == TransactionType.RESERVE,
                                Ledger.amount,
                            ),
                            else_=D0,
                        )
                    )
                ).label("reserved_amount"),
                Job.usage_params["count"].label("count"),
                Job.reservation_params["count"].label("reserved_count"),
                case(
                    (Job.finished_at == Job.started_at, None),
                    else_=func.extract("epoch", (Job.finished_at - Job.started_at)).cast(Integer),
                ).label("duration"),
                Job.reservation_params["duration"].label("reserved_duration"),
                Job.usage_params["size"].label("size"),
            )
            .select_from(selected_job_query)
            .join(Job, Job.id == selected_job_query.c.id)
            .outerjoin(Journal, Journal.job_id == Job.id)
            .outerjoin(
                Ledger, and_(Ledger.journal_id == Journal.id, Ledger.account_id == Job.proj_id)
            )
            .group_by(Job.id)
            .order_by(*order_by_columns)
        )
        return (await self.db.execute(query)).all(), count
