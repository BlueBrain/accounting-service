"""Reservation api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    ApiResponse,
    LongrunReservationIn,
    OneshotReservationIn,
    ReservationOut,
)
from app.service import reservation

router = APIRouter()


@router.post("/oneshot", status_code=status.HTTP_201_CREATED)
async def make_oneshot_reservation(
    repos: RepoGroupDep,
    reservation_request: OneshotReservationIn,
) -> ApiResponse[ReservationOut]:
    """Make a new reservation for oneshot job."""
    result = await reservation.make_oneshot_reservation(repos, reservation_request)
    return ApiResponse(
        message="Oneshot reservation executed",
        data=result,
    )


@router.post("/longrun", status_code=status.HTTP_201_CREATED)
async def make_longrun_reservation(
    repos: RepoGroupDep,
    reservation_request: LongrunReservationIn,
) -> ApiResponse[ReservationOut]:
    """Make a new reservation for longrun job."""
    result = await reservation.make_longrun_reservation(repos, reservation_request)
    return ApiResponse(
        message="Longrun reservation executed",
        data=result,
    )
