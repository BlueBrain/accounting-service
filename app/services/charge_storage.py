"""Charge for storage."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Row

from app.constants import D0, TransactionType
from app.logger import get_logger
from app.repositories.group import RepositoryGroup
from app.schemas.domain import ChargeStorageResult
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


async def _charge_new_storage_jobs(
    repos: RepositoryGroup,
    ids: set[UUID],
    not_charged: dict[UUID, Row],
) -> None:
    now = utcnow()
    system_account = await repos.account.get_system_account()
    for proj_id in ids:
        job = not_charged[proj_id]
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=proj_id)
        amount = _get_amount(
            total_seconds=(now - job.started_at).total_seconds(),
            total_bytes=job.units,
        )
        await repos.ledger.insert_transaction(
            amount=amount,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_STORAGE,
            job_id=job.id,
            properties={"reason": "new"},
        )
        await repos.job.update_job(
            job_id=job.id, vlab_id=accounts.vlab.id, proj_id=proj_id, last_charged_at=now
        )
        await repos.db.commit()


async def _charge_running_storage_jobs(
    repos: RepositoryGroup,
    ids: set[UUID],
    last_charged: dict[UUID, Row],
    min_charging_interval: float,
    min_charging_amount: Decimal,
) -> None:
    now = utcnow()
    system_account = await repos.account.get_system_account()
    for proj_id in ids:
        job = last_charged[proj_id]
        total_seconds = (now - job.last_charged_at).total_seconds()
        if total_seconds < min_charging_interval:
            L.debug(
                "Ignoring charge for project %s: elapsed seconds since last charge: %.3f",
                proj_id,
                total_seconds,
            )
            continue
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=proj_id)
        amount = _get_amount(
            total_seconds=total_seconds,
            total_bytes=job.units,
        )
        if abs(amount) < min_charging_amount:
            L.debug(
                "Ignoring charge for project %s: calculated amount too low: %.6f",
                proj_id,
                amount,
            )
            continue
        await repos.ledger.insert_transaction(
            amount=amount,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_STORAGE,
            job_id=job.id,
            properties={"reason": "running"},
        )
        await repos.job.update_job(
            job_id=job.id, vlab_id=accounts.vlab.id, proj_id=proj_id, last_charged_at=now
        )
        await repos.db.commit()


async def _charge_transitioning_storage_jobs(
    repos: RepositoryGroup,
    ids: set[UUID],
    not_charged: dict[UUID, Row],
    last_charged: dict[UUID, Row],
) -> None:
    now = utcnow()
    system_account = await repos.account.get_system_account()
    for proj_id in ids:
        not_charged_job = not_charged[proj_id]
        last_charged_job = last_charged[proj_id]
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=proj_id)
        # next_amount should be always positive
        next_amount = _get_amount(
            total_seconds=(now - not_charged_job.started_at).total_seconds(),
            total_bytes=not_charged_job.units,
        )
        # prev_amount is negative if not_charged_job.started_at < last_charged_job.last_charged_at,
        # i.e. when multiple jobs have been inserted before the existing ones have been processed
        prev_amount = _get_amount(
            total_seconds=(
                not_charged_job.started_at - last_charged_job.last_charged_at
            ).total_seconds(),
            total_bytes=last_charged_job.units,
        )
        # adjustment is negative if not_charged_job.units < last_charged_job.units
        adjustment = _get_amount(
            total_seconds=(
                not_charged_job.started_at - last_charged_job.started_at
            ).total_seconds(),
            total_bytes=not_charged_job.units - last_charged_job.units,
        )
        await repos.ledger.insert_transaction(
            amount=prev_amount,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_STORAGE,
            job_id=last_charged_job.id,
            properties={"reason": "close"},
        )
        await repos.ledger.insert_transaction(
            amount=adjustment,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_STORAGE,
            job_id=last_charged_job.id,
            properties={"reason": "adjust"},
        )
        await repos.ledger.insert_transaction(
            amount=next_amount,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_STORAGE,
            job_id=not_charged_job.id,
            properties={"reason": "open"},
        )
        await repos.job.update_job(
            job_id=not_charged_job.id,
            vlab_id=accounts.vlab.id,
            proj_id=proj_id,
            last_charged_at=now,
        )
        await repos.job.update_job(
            job_id=last_charged_job.id,
            vlab_id=accounts.vlab.id,
            proj_id=proj_id,
            last_charged_at=now,
        )
        await repos.db.commit()


async def charge_storage_jobs(
    repos: RepositoryGroup,
    min_charging_interval: float = 0.0,
    min_charging_amount: Decimal = D0,
) -> ChargeStorageResult:
    """Charge for the storage.

    Args:
        repos: repository group instance.
        min_charging_interval: minimum interval between charges for running jobs.
            It doesn't affect new and transitioning jobs.
        min_charging_amount: minimum amount of money to be charged for running jobs.
            It doesn't affect new and transitioning jobs.

    Description:
        - For each project:
          - get the record with maximum last_charged_at not null -> assign to J1=last_charged
          - get the record with last_charged_at=null, and minimum started_at in case there are
            multiple records with last_charged_at=null -> assign to J2=not_charged
        - If a project has J2 but not J1:
          - charge J2.units for the time (now - J2.started_at)
          - update J2.last_charged_at
        - If a project has J1 but not J2:
          - charge J1.units for the time (now - J1.last_charged_at)
          - update J1.last_charged_at
        - If a project has J1 and J2, charge for a compound amount:
          - next_amount: charge J2.units for (J2.last_charged_at - J2.started_at)
          - prev_amount: charge J1.units for (J2.started_at - J1.last_charged_at)
          - adjustment: charge (J2.units - J1.units) for (J2.started_at - J1.started_at)
          - update J1.last_charged_at
          - update J2.last_charged_at
    """
    not_charged = await repos.job.get_storage_jobs_not_charged()  # J2
    last_charged = await repos.job.get_storage_jobs_last_charged()  # J1
    new_ids = not_charged.keys() - last_charged.keys()  # in J2 but not in J1
    running_ids = last_charged.keys() - not_charged.keys()  # in J1 but not in J2
    transitioning_ids = last_charged.keys() & not_charged.keys()  # in both J2 and J1
    await _charge_new_storage_jobs(
        repos,
        new_ids,
        not_charged=not_charged,
    )
    await _charge_running_storage_jobs(
        repos,
        running_ids,
        last_charged=last_charged,
        min_charging_interval=min_charging_interval,
        min_charging_amount=min_charging_amount,
    )
    await _charge_transitioning_storage_jobs(
        repos,
        transitioning_ids,
        not_charged=not_charged,
        last_charged=last_charged,
    )
    return ChargeStorageResult(
        not_charged=len(not_charged),
        last_charged=len(last_charged),
        new_ids=len(new_ids),
        running_ids=len(running_ids),
        transitioning_ids=len(transitioning_ids),
    )
