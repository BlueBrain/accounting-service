"""Reservation service."""

from app.constants import AccountType, TransactionType
from app.logger import get_logger
from app.repositories.group import RepositoryGroup
from app.schemas.api import (
    LongJobsReservationRequest,
    ReservationRequest,
    ReservationResponse,
    ShortJobsReservationRequest,
)
from app.services.price import calculate_running_cost
from app.utils import create_uuid, utcnow

L = get_logger(__name__)


async def _make_reservation(
    repos: RepositoryGroup,
    reservation_request: ReservationRequest,
    reserved_units: int,
) -> ReservationResponse:
    """Make the job reservation."""
    # retrieve the accounts while locking the project account against concurrent updates
    accounts = await repos.account.get_accounts_by_proj_id(
        proj_id=reservation_request.proj_id, for_update={AccountType.PROJ}
    )
    available_amount = accounts.proj.balance
    requested_amount = await calculate_running_cost(
        vlab_id=accounts.vlab.id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        units=reserved_units,
    )
    if requested_amount > available_amount:
        L.info(
            "Reservation not allowed for project %s: requested=%s, available=%s",
            accounts.proj.id,
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
    await repos.job.insert_job(
        job_id=job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        reserved_units=reserved_units,
        reserved_at=now,
        properties=None,
    )
    await repos.ledger.insert_transaction(
        amount=requested_amount,
        debited_from=accounts.proj.id,
        credited_to=accounts.rsv.id,
        transaction_datetime=now,
        transaction_type=TransactionType.RESERVE,
        job_id=job_id,
        properties=None,
    )
    L.info(
        "Reservation allowed for project %s: requested=%s, available=%s, job_id=%s",
        accounts.proj.id,
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
    repos: RepositoryGroup,
    reservation_request: ShortJobsReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a short job."""
    units = reservation_request.count
    return await _make_reservation(repos, reservation_request, reserved_units=units)


async def make_long_jobs_reservation(
    repos: RepositoryGroup,
    reservation_request: LongJobsReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a long job."""
    requested_time = 10  # TODO: define the logic to calculate the requested time and cost
    units = reservation_request.instances * requested_time
    return await _make_reservation(repos, reservation_request, reserved_units=units)
