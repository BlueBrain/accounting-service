"""Charge for long jobs."""

from datetime import datetime
from decimal import Decimal

from app.constants import D0, TransactionType
from app.db.model import Job
from app.db.utils import try_nested
from app.logger import L
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeLongJobResult, StartedJob
from app.service.pricing import calculate_fixed_cost, calculate_running_cost
from app.utils import utcnow


async def _charge_generic(
    repos: RepositoryGroup,
    job: StartedJob,
    *,
    charge_from: datetime,
    charge_to: datetime,
    add_fixed_cost: bool,
    release_reservation: bool,
    reason: str,
    min_charging_interval: float = 0.0,
    min_charging_amount: Decimal = D0,
) -> None:
    now = utcnow()
    total_seconds = (charge_to - charge_from).total_seconds()
    if 0 < total_seconds < min_charging_interval:
        L.debug(
            "Not charging job {}: elapsed seconds since last charge: {:.3f}",
            job.id,
            total_seconds,
        )
        return
    instances = int((job.properties or {}).get("instances", 1))
    value_to_be_charged = int(total_seconds * instances)
    system_account = await repos.account.get_system_account()
    accounts = await repos.account.get_accounts_by_proj_id(proj_id=job.proj_id)
    running_amount_to_be_charged = await calculate_running_cost(
        vlab_id=accounts.vlab.id,
        service_type=job.service_type,
        service_subtype=job.service_subtype,
        usage_value=value_to_be_charged,
    )
    fixed_amount_to_be_charged = (
        await calculate_fixed_cost(
            vlab_id=accounts.vlab.id,
            service_type=job.service_type,
            service_subtype=job.service_subtype,
        )
        if add_fixed_cost
        else D0
    )
    remaining_reservation = await repos.ledger.get_remaining_reservation_for_job(
        job_id=job.id, account_id=accounts.rsv.id
    )
    if remaining_reservation < 0:
        err = f"Reservation for job {job.id} is negative: {remaining_reservation}"
        raise RuntimeError(err)
    total_amount = running_amount_to_be_charged + fixed_amount_to_be_charged
    if abs(total_amount) < min_charging_amount:
        L.debug(
            "Not charging job {}: calculated amount too low: {:.6f}",
            job.id,
            total_amount,
        )
        return
    if total_amount > 0:
        reservation_amount_to_be_charged = min(total_amount, remaining_reservation)
        project_amount_to_be_charged = max(total_amount - reservation_amount_to_be_charged, D0)
        remaining_reservation -= reservation_amount_to_be_charged
    else:
        # the job has been previously overcharged
        reservation_amount_to_be_charged = D0
        project_amount_to_be_charged = total_amount

    if reservation_amount_to_be_charged > 0:
        await repos.ledger.insert_transaction(
            amount=reservation_amount_to_be_charged,
            debited_from=accounts.rsv.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_LONG_JOB,
            job_id=job.id,
            properties={"reason": f"{reason}:charge_reservation"},
        )
    if project_amount_to_be_charged > 0:
        await repos.ledger.insert_transaction(
            amount=project_amount_to_be_charged,
            debited_from=accounts.proj.id,
            credited_to=system_account.id,
            transaction_datetime=now,
            transaction_type=TransactionType.CHARGE_LONG_JOB,
            job_id=job.id,
            properties={"reason": f"{reason}:charge_project"},
        )
    elif project_amount_to_be_charged < 0:
        await repos.ledger.insert_transaction(
            amount=project_amount_to_be_charged * -1,
            debited_from=system_account.id,
            credited_to=accounts.proj.id,
            transaction_datetime=now,
            transaction_type=TransactionType.REFUND,
            job_id=job.id,
            properties={"reason": f"{reason}:refund_project"},
        )
    if release_reservation and remaining_reservation > 0:
        await repos.ledger.insert_transaction(
            amount=remaining_reservation,
            debited_from=accounts.rsv.id,
            credited_to=accounts.proj.id,
            transaction_datetime=now,
            transaction_type=TransactionType.RELEASE,
            job_id=job.id,
            properties={"reason": f"{reason}:release_reservation"},
        )
    await repos.job.update_job(
        job_id=job.id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        last_charged_at=charge_to,
        usage_value=Job.usage_value + value_to_be_charged,
    )


async def charge_long_job(
    repos: RepositoryGroup,
    min_charging_interval: float = 0.0,
    min_charging_amount: Decimal = D0,
) -> ChargeLongJobResult:
    """Charge for long jobs.

    Args:
        repos: repository group instance.
        min_charging_interval: minimum interval between charges for running jobs.
            It doesn't affect finished jobs.
        min_charging_amount: minimum amount of money to be charged for running jobs.
            It doesn't affect finished jobs.
    """

    def _on_error() -> None:
        L.exception("Error processing long job {}", job.id)
        result.failure += 1

    now = utcnow()
    result = ChargeLongJobResult()
    jobs = await repos.job.get_long_jobs_to_be_charged()
    for job in jobs:
        async with try_nested(repos.db, on_error=_on_error):
            match job:
                case StartedJob(last_charged_at=None, finished_at=None):
                    # Charge fixed cost and first running time, set last_charged_at=now
                    await _charge_generic(
                        repos,
                        job,
                        charge_from=job.started_at,
                        charge_to=now,
                        add_fixed_cost=True,
                        release_reservation=False,
                        reason="unfinished_uncharged",
                        min_charging_interval=min_charging_interval,
                        min_charging_amount=min_charging_amount,
                    )
                    result.unfinished_uncharged += 1
                case StartedJob(last_charged_at=datetime() as last_charged_at, finished_at=None):
                    # Charge running time since the last charge, set last_charged_at=now
                    await _charge_generic(
                        repos,
                        job,
                        charge_from=last_charged_at,
                        charge_to=now,
                        add_fixed_cost=False,
                        release_reservation=False,
                        reason="unfinished_charged",
                        min_charging_interval=min_charging_interval,
                        min_charging_amount=min_charging_amount,
                    )
                    result.unfinished_charged += 1
                case StartedJob(last_charged_at=None, finished_at=datetime() as finished_at):
                    # Charge fixed costs and full running time, set last_charged_at=finished_at,
                    # release reservation
                    await _charge_generic(
                        repos,
                        job,
                        charge_from=job.started_at,
                        charge_to=finished_at,
                        add_fixed_cost=True,
                        release_reservation=True,
                        reason="finished_uncharged",
                    )
                    result.finished_uncharged += 1
                case StartedJob(last_charged_at=last_charged_at, finished_at=finished_at) if (
                    last_charged_at and finished_at and last_charged_at < finished_at
                ):
                    # Charge remaining running time, set last_charged_at=finished_at,
                    # release reservation
                    await _charge_generic(
                        repos,
                        job,
                        charge_from=last_charged_at,
                        charge_to=finished_at,
                        add_fixed_cost=False,
                        release_reservation=True,
                        reason="finished_charged",
                    )
                    result.finished_charged += 1
                case StartedJob(last_charged_at=last_charged_at, finished_at=finished_at) if (
                    last_charged_at and finished_at and last_charged_at > finished_at
                ):
                    # Refund extra time already charged, set last_charged_at=finished_at, release
                    # reservation. This can happen if the event notifying the completion of the job
                    # has been processed too late, and some amount of money has already been charged
                    # by the periodic charger.
                    await _charge_generic(
                        repos,
                        job,
                        charge_from=last_charged_at,
                        charge_to=finished_at,
                        add_fixed_cost=False,
                        release_reservation=True,
                        reason="finished_overcharged",
                    )
                    result.finished_overcharged += 1
                case _:
                    err = f"Pattern not matched for job {job.id}"
                    raise ValueError(err)
    return result
