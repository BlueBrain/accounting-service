"""Reservation api."""

from fastapi import APIRouter

from app.dependencies import RepoGroupDep
from app.schema.api import (
    LongJobsReservationRequest,
    ReservationResponse,
    ShortJobsReservationRequest,
)
from app.service import reservation

router = APIRouter()


@router.post("/short-jobs")
async def make_short_jobs_reservation(
    repos: RepoGroupDep,
    reservation_request: ShortJobsReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a short job."""
    return await reservation.make_short_jobs_reservation(repos, reservation_request)


@router.post("/long-jobs")
async def make_long_jobs_reservation(
    repos: RepoGroupDep,
    reservation_request: LongJobsReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for a long job."""
    return await reservation.make_long_jobs_reservation(repos, reservation_request)
