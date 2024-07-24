"""Reservation service."""

from app.constants import AccountType, TransactionType
from app.logger import L
from app.repository.group import RepositoryGroup
from app.schema.api import (
    LongJobReservationRequest,
    ReservationRequest,
    ReservationResponse,
    ShortJobReservationRequest,
)
from app.service.pricing import calculate_running_cost
from app.utils import create_uuid, utcnow


async def _make_reservation(
    repos: RepositoryGroup,
    reservation_request: ReservationRequest,
    usage_value: int,
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
        usage_value=usage_value,
    )
    if requested_amount > available_amount:
        L.info(
            "Reservation not allowed for project {}: requested={}, available={}",
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
        usage_value=usage_value,
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
        "Reservation allowed for project {}: requested={}, available={}, job_id={}",
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


async def make_short_job_reservation(
    repos: RepositoryGroup,
    reservation_request: ShortJobReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a short job."""
    usage_value = reservation_request.count
    return await _make_reservation(repos, reservation_request, usage_value=usage_value)


async def make_long_job_reservation(
    repos: RepositoryGroup,
    reservation_request: LongJobReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a long job."""
    requested_time = 10  # TODO: define the logic to calculate the requested time and cost
    usage_value = reservation_request.instances * requested_time
    return await _make_reservation(repos, reservation_request, usage_value=usage_value)
