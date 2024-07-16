"""Charge for short jobs."""

from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import D0, TransactionType
from app.db.models import Job
from app.logger import get_logger
from app.repositories.group import RepositoryGroup
from app.schemas.domain import ChargeShortJobsResult
from app.services.pricing import calculate_running_cost
from app.utils import utcnow

L = get_logger(__name__)


@asynccontextmanager
async def _savepoint(db: AsyncSession, job_id: UUID) -> AsyncIterator[None]:
    try:
        async with db.begin_nested():
            yield
    except Exception:  # noqa: BLE001
        L.exception("Error when processing job %s", job_id)


async def _charge_generic(
    repos: RepositoryGroup,
    job: Job,
    *,
    last_charged_at: datetime,
    reason: str,
) -> None:
    system_account = await repos.account.get_system_account()
    accounts = await repos.account.get_accounts_by_proj_id(proj_id=job.proj_id)
    total_amount = await calculate_running_cost(
        vlab_id=accounts.vlab.id,
        service_type=job.service_type,
        service_subtype=job.service_subtype,
        units=job.units,
    )
    remaining_reservation = await repos.ledger.get_remaining_reservation_for_job(
        job_id=job.id, account_id=accounts.rsv.id
    )
    if remaining_reservation < 0:
        err = f"Reservation for job {job.id} is negative: {remaining_reservation}"
        raise RuntimeError(err)
    if total_amount < 0:
        err = f"Total amount for job {job.id} is negative: {total_amount}"
        raise RuntimeError(err)
    reservation_amount_to_be_charged = min(total_amount, remaining_reservation)
    project_amount_to_be_charged = max(total_amount - reservation_amount_to_be_charged, D0)
    remaining_reservation -= reservation_amount_to_be_charged
    if reservation_amount_to_be_charged > 0:
        await repos.ledger.insert_transaction(
            amount=reservation_amount_to_be_charged,
            debited_from=accounts.rsv.id,
            credited_to=system_account.id,
            transaction_datetime=last_charged_at,
            transaction_type=TransactionType.CHARGE_SHORT_JOBS,
            job_id=job.id,
            properties={"reason": f"{reason}:charge_reservation"},
        )
    if project_amount_to_be_charged > 0:
        await repos.ledger.insert_transaction(
            amount=project_amount_to_be_charged,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=last_charged_at,
            transaction_type=TransactionType.CHARGE_SHORT_JOBS,
            job_id=job.id,
            properties={"reason": f"{reason}:charge_project"},
        )
    if remaining_reservation > 0:
        await repos.ledger.insert_transaction(
            amount=remaining_reservation,
            debited_from=accounts.rsv.id,
            credited_to=accounts.proj.id,
            transaction_datetime=last_charged_at,
            transaction_type=TransactionType.RELEASE,
            job_id=job.id,
            properties={"reason": f"{reason}:release_reservation"},
        )
    await repos.job.update_job(
        job_id=job.id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        last_charged_at=last_charged_at,
    )


async def charge_short_jobs(
    repos: RepositoryGroup,
    jobs: Sequence[Job] | None = None,
) -> ChargeShortJobsResult:
    """Charge for short jobs.

    Args:
        repos: repository group instance.
        jobs: optional sequence of jobs.
    """
    now = utcnow()
    result = ChargeShortJobsResult()
    jobs = jobs or await repos.job.get_short_jobs_to_be_charged()
    for job in jobs:
        async with _savepoint(repos.db, job.id):
            await _charge_generic(repos, job, last_charged_at=now, reason="finished_uncharged")
            result.finished_uncharged += 1
    return result
