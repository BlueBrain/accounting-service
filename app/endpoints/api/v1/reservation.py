"""Reservation endpoints."""

from fastapi import APIRouter

from app.dependencies import AccountRepoDep, JobRepoDep, LedgerRepoDep
from app.schemas.api import (
    LongJobsReservationRequest,
    ReservationResponse,
    ShortJobsReservationRequest,
)
from app.services import reservation

router = APIRouter()


@router.post("/short_jobs")
async def make_short_jobs_reservation(
    reservation_request: ShortJobsReservationRequest,
    account_repo: AccountRepoDep,
    job_repo: JobRepoDep,
    ledger_repo: LedgerRepoDep,
) -> ReservationResponse:
    """Make a new reservation for a short job."""
    return await reservation.make_short_jobs_reservation(
        reservation_request,
        account_repo=account_repo,
        job_repo=job_repo,
        ledger_repo=ledger_repo,
    )


@router.post("/long_jobs")
async def make_long_jobs_reservation(
    reservation_request: LongJobsReservationRequest,
    account_repo: AccountRepoDep,
    job_repo: JobRepoDep,
    ledger_repo: LedgerRepoDep,
) -> ReservationResponse:
    """Make a new reservation for a long job."""
    return await reservation.make_long_jobs_reservation(
        reservation_request,
        account_repo=account_repo,
        job_repo=job_repo,
        ledger_repo=ledger_repo,
    )
