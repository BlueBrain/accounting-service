"""Charge for storage."""

from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from app.constants import D0, TransactionType
from app.db.utils import try_nested
from app.logger import get_logger
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeStorageResult, StartedJob
from app.utils import utcnow

L = get_logger(__name__)


def _get_price_per_gb_per_day() -> Decimal:
    # TODO: to be retrieved from db
    return round(Decimal("0.023") / 30, ndigits=10)


def _get_amount(total_seconds: float, total_bytes: float) -> Decimal:
    return round(
        Decimal(total_seconds / 24 / 3600 * total_bytes / 1024**3) * _get_price_per_gb_per_day(),
        ndigits=10,
    )


async def _charge_one(
    repos: RepositoryGroup,
    job: StartedJob,
    min_charging_interval: float,
    min_charging_amount: Decimal,
    properties: dict[str, Any] | None = None,
) -> None:
    charging_at = job.finished_at or utcnow()
    total_seconds = (charging_at - (job.last_charged_at or job.started_at)).total_seconds()
    if not job.finished_at and total_seconds < min_charging_interval:
        L.debug(
            "Not charging job %s: elapsed seconds since last charge: %.3f",
            job.id,
            total_seconds,
        )
        return
    system_account = await repos.account.get_system_account()
    accounts = await repos.account.get_accounts_by_proj_id(proj_id=job.proj_id)
    amount = _get_amount(
        total_seconds=total_seconds,
        total_bytes=job.units,
    )
    if not job.finished_at and abs(amount) < min_charging_amount:
        L.debug(
            "Not charging job %s: calculated amount too low: %.6f",
            job.id,
            amount,
        )
        return
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=accounts.proj.id,
        credited_to=system_account.id,
        transaction_datetime=charging_at,
        transaction_type=TransactionType.CHARGE_STORAGE,
        job_id=job.id,
        properties=properties,
    )
    await repos.job.update_job(
        job_id=job.id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        last_charged_at=charging_at,
    )


async def charge_storage_jobs(
    repos: RepositoryGroup,
    jobs: Sequence[StartedJob],
    min_charging_interval: float = 0.0,
    min_charging_amount: Decimal = D0,
) -> ChargeStorageResult:
    """Charge for the storage and update the corresponding job.

    Args:
        repos: repository group instance.
        jobs: sequence of jobs to be processed, or None to select all the job not finished yet.
        min_charging_interval: minimum interval between charges for running jobs.
        min_charging_amount: minimum amount of money to be charged for running jobs.
    """

    def _on_error() -> None:
        L.exception("Error processing storage job %s", job.id)
        result.failure += 1

    def _on_success() -> None:
        result.success += 1

    result = ChargeStorageResult()
    for job in jobs:
        async with try_nested(repos.db, on_error=_on_error, on_success=_on_success):
            await _charge_one(
                repos=repos,
                job=job,
                min_charging_interval=min_charging_interval,
                min_charging_amount=min_charging_amount,
            )
    return result
