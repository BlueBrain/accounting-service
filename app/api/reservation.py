"""Reservation api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    LongrunReservationRequest,
    OneshotReservationRequest,
    ReservationResponse,
)
from app.service import reservation

router = APIRouter()


@router.post("/oneshot", status_code=status.HTTP_201_CREATED)
async def make_oneshot_reservation(
    repos: RepoGroupDep,
    reservation_request: OneshotReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for oneshot job."""
    return await reservation.make_oneshot_reservation(repos, reservation_request)


@router.post("/longrun", status_code=status.HTTP_201_CREATED)
async def make_longrun_reservation(
    repos: RepoGroupDep,
    reservation_request: LongrunReservationRequest,
) -> ReservationResponse:
    """Make a new reservation for longrun job."""
    return await reservation.make_longrun_reservation(repos, reservation_request)
