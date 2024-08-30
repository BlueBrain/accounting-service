"""Job report repository module."""

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Row, case, func

from app.constants import D0, TransactionType
from app.db.model import Job, Journal, Ledger
from app.repository.base import BaseRepository


class ReportRepository(BaseRepository):
    """ReportRepository."""

    async def get_job_reports(self, proj_id: UUID) -> Sequence[Row]:
        """Get the list of job reports for a given project."""
        query = (
            sa.select(
                Job.id.label("job_id"),
                Job.service_type.label("type"),
                Job.service_subtype.label("subtype"),
                Job.reserved_at,
                Job.started_at,
                Job.finished_at,
                Job.cancelled_at,
                (-func.sum(Ledger.amount)).label("amount"),
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
                Job.usage_params["duration"].label("duration"),
                Job.reservation_params["duration"].label("reserved_duration"),
                Job.usage_params["size"].label("size"),
                Job.reservation_params["size"].label("reserved_size"),
            )
            .select_from(Job)
            .join(Journal)
            .join(Ledger)
            .where(
                Job.proj_id == proj_id,
                Job.finished_at == Job.last_charged_at,
                Ledger.account_id == proj_id,
            )
            .group_by(Job.id)
            .order_by(Job.started_at)
        )
        return (await self.db.execute(query)).all()
