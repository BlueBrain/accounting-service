"""Release service."""

from decimal import Decimal
from http import HTTPStatus
from uuid import UUID

from app.constants import ServiceType, TransactionType
from app.errors import ApiError, ApiErrorCode, ensure_result
from app.repository.group import RepositoryGroup
from app.utils import utcnow


async def _release_reservation(
    repos: RepositoryGroup,
    job_id: UUID,
    service_type: ServiceType,
) -> Decimal:
    now = utcnow()
    job = await repos.job.get_job(job_id=job_id, for_update=True)
    if job is None or job.service_type != service_type:
        raise ApiError(
            message="The specified job cannot be found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        )
    if job.started_at:
        raise ApiError(
            message="The reservation cannot be released because already started",
            error_code=ApiErrorCode.JOB_ALREADY_STARTED,
        )
    if job.cancelled_at:
        raise ApiError(
            message="The reservation cannot be released because already cancelled",
            error_code=ApiErrorCode.JOB_ALREADY_CANCELLED,
        )
    with ensure_result(error_message="Account not found"):
        accounts = await repos.account.get_accounts_by_proj_id(proj_id=job.proj_id)
    remaining_reservation = await repos.ledger.get_remaining_reservation_for_job(
        job_id=job.id, account_id=accounts.rsv.id, raise_if_negative=True
    )
    if remaining_reservation > 0:
        await repos.ledger.insert_transaction(
            amount=remaining_reservation,
            debited_from=accounts.rsv.id,
            credited_to=accounts.proj.id,
            transaction_datetime=now,
            transaction_type=TransactionType.RELEASE,
            job_id=job.id,
            properties={"reason": "job_cancelled:release_reservation"},
        )
    await repos.job.update_job(
        job_id=job_id,
        vlab_id=accounts.vlab.id,
        proj_id=accounts.proj.id,
        cancelled_at=now,
    )
    return remaining_reservation


async def release_oneshot_reservation(repos: RepositoryGroup, job_id: UUID) -> Decimal:
    """Release a reservation for oneshot job."""
    return await _release_reservation(repos, job_id=job_id, service_type=ServiceType.ONESHOT)


async def release_longrun_reservation(repos: RepositoryGroup, job_id: UUID) -> Decimal:
    """Release a reservation for longrun job."""
    return await _release_reservation(repos, job_id=job_id, service_type=ServiceType.LONGRUN)
