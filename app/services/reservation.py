"""Reservation service."""

from app.constants import TransactionType
from app.logger import get_logger
from app.repositories.account import AccountRepository
from app.repositories.job import JobRepository
from app.repositories.ledger import LedgerRepository
from app.schemas import (
    LongJobsReservationRequest,
    ReservationRequest,
    ReservationResponse,
    ShortJobsReservationRequest,
)
from app.services.price import get_price
from app.utils import create_uuid, utcnow

L = get_logger(__name__)


async def _make_reservation(
    reservation_request: ReservationRequest,
    reserved_units: int,
    account_repo: AccountRepository,
    job_repo: JobRepository,
    ledger_repo: LedgerRepository,
) -> ReservationResponse:
    """Make the job reservation."""
    # lock the project row against concurrent updates
    proj_account = await account_repo.get_proj_account(
        proj_id=reservation_request.proj_id, for_update=True
    )
    reservation_account = await account_repo.get_reservation_account(
        proj_id=reservation_request.proj_id
    )
    proj_id = proj_account.id
    vlab_id = proj_account.parent_id
    available_amount = proj_account.balance
    requested_amount = await get_price(
        vlab_id=vlab_id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        units=reserved_units,
    )
    if requested_amount > available_amount:
        L.info(
            "Reservation not allowed for project %s: requested=%s, available=%s",
            reservation_account.id,
            requested_amount,
            available_amount,
        )
        return ReservationResponse(
            is_allowed=False,
            requested_amount=requested_amount,
            available_amount=available_amount,
        )
    job_id = create_uuid()
    now = utcnow()
    await job_repo.insert_job(
        job_id=job_id,
        vlab_id=vlab_id,
        proj_id=proj_id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        reserved_units=reserved_units,
        reserved_at=now,
        properties=None,
    )
    await ledger_repo.insert_transaction(
        amount=requested_amount,
        debited_from=proj_account.id,
        credited_to=reservation_account.id,
        transaction_datetime=now,
        transaction_type=TransactionType.RESERVE,
        job_id=job_id,
        properties=None,
    )
    L.info(
        "Reservation allowed for project %s: requested=%s, available=%s, job_id=%s",
        reservation_account.id,
        requested_amount,
        available_amount,
        job_id,
    )
    return ReservationResponse(
        is_allowed=True,
        requested_amount=requested_amount,
        available_amount=available_amount,
        job_id=job_id,
    )


async def make_short_jobs_reservation(
    reservation_request: ShortJobsReservationRequest,
    account_repo: AccountRepository,
    job_repo: JobRepository,
    ledger_repo: LedgerRepository,
) -> ReservationResponse:
    """Make a new reservation for a short job."""
    units = reservation_request.count
    return await _make_reservation(
        reservation_request,
        reserved_units=units,
        account_repo=account_repo,
        job_repo=job_repo,
        ledger_repo=ledger_repo,
    )


async def make_long_jobs_reservation(
    reservation_request: LongJobsReservationRequest,
    account_repo: AccountRepository,
    job_repo: JobRepository,
    ledger_repo: LedgerRepository,
) -> ReservationResponse:
    """Make a new reservation for a long job."""
    requested_time = 10  # TODO: define the logic to calculate the requested time and cost
    units = reservation_request.instances * requested_time
    return await _make_reservation(
        reservation_request,
        reserved_units=units,
        account_repo=account_repo,
        job_repo=job_repo,
        ledger_repo=ledger_repo,
    )
