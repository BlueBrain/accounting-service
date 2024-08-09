"""Reservation service."""

from typing import Any

from app.constants import AccountType, TransactionType
from app.logger import L
from app.repository.group import RepositoryGroup
from app.schema.api import (
    LongrunReservationRequest,
    OneshotReservationRequest,
    ReservationRequest,
    ReservationResponse,
)
from app.service.price import calculate_cost
from app.service.usage import calculate_longrun_usage_value, calculate_oneshot_usage_value
from app.utils import create_uuid, utcnow


async def _make_reservation(
    repos: RepositoryGroup,
    reservation_request: ReservationRequest,
    usage_value: int,
    reservation_params: dict[str, Any],
) -> ReservationResponse:
    """Make the job reservation."""
    reserving_at = utcnow()
    # retrieve the accounts while locking the project account against concurrent updates
    accounts = await repos.account.get_accounts_by_proj_id(
        proj_id=reservation_request.proj_id, for_update={AccountType.PROJ}
    )
    available_amount = accounts.proj.balance
    price = await repos.price.get_price(
        vlab_id=accounts.vlab.id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        usage_datetime=reserving_at,
    )
    requested_amount = calculate_cost(price=price, usage_value=usage_value)
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
    await repos.job.insert_job(
        job_id=job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        service_type=reservation_request.type,
        service_subtype=reservation_request.subtype,
        reserved_at=reserving_at,
        reservation_params=reservation_params,
    )
    await repos.ledger.insert_transaction(
        amount=requested_amount,
        debited_from=accounts.proj.id,
        credited_to=accounts.rsv.id,
        transaction_datetime=reserving_at,
        transaction_type=TransactionType.RESERVE,
        job_id=job_id,
        price_id=price.id,
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


async def make_oneshot_reservation(
    repos: RepositoryGroup,
    reservation_request: OneshotReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for oneshot job."""
    usage_value = calculate_oneshot_usage_value(
        count=reservation_request.count,
    )
    return await _make_reservation(
        repos,
        reservation_request,
        usage_value=usage_value,
        reservation_params={
            "count": reservation_request.count,
        },
    )


async def make_longrun_reservation(
    repos: RepositoryGroup,
    reservation_request: LongrunReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for longrun job."""
    usage_value = calculate_longrun_usage_value(
        instances=reservation_request.instances,
        instance_type=reservation_request.instance_type,
        duration=reservation_request.duration,
    )
    return await _make_reservation(
        repos,
        reservation_request,
        usage_value=usage_value,
        reservation_params={
            "duration": reservation_request.duration,
            "instances": reservation_request.instances,
            "instance_type": reservation_request.instance_type,
        },
    )
