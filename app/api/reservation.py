"""Reservation api."""

from uuid import UUID

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    ApiResponse,
    MakeLongrunReservationIn,
    MakeOneshotReservationIn,
    MakeReservationOut,
    ReleaseReservationOut,
)
from app.service import release, reservation

router = APIRouter()


@router.post("/oneshot", status_code=status.HTTP_201_CREATED)
async def make_oneshot_reservation(
    repos: RepoGroupDep,
    reservation_request: MakeOneshotReservationIn,
) -> ApiResponse[MakeReservationOut]:
    """Make a new reservation for oneshot job."""
    result = await reservation.make_oneshot_reservation(repos, reservation_request)
    return ApiResponse[MakeReservationOut](
        message="Oneshot reservation executed",
        data=result,
    )


@router.post("/longrun", status_code=status.HTTP_201_CREATED)
async def make_longrun_reservation(
    repos: RepoGroupDep,
    reservation_request: MakeLongrunReservationIn,
) -> ApiResponse[MakeReservationOut]:
    """Make a new reservation for longrun job."""
    result = await reservation.make_longrun_reservation(repos, reservation_request)
    return ApiResponse[MakeReservationOut](
        message="Longrun reservation executed",
        data=result,
    )


@router.delete("/oneshot/{job_id}")
async def release_oneshot_reservation(
    repos: RepoGroupDep,
    job_id: UUID,
) -> ApiResponse[ReleaseReservationOut]:
    """Release the reservation for oneshot job."""
    reservation_amount = await release.release_oneshot_reservation(repos, job_id=job_id)
    return ApiResponse[ReleaseReservationOut](
        message="Oneshot reservation has been released",
        data=ReleaseReservationOut(
            job_id=job_id,
            amount=reservation_amount,
        ),
    )


@router.delete("/longrun/{job_id}")
async def release_longrun_reservation(
    repos: RepoGroupDep,
    job_id: UUID,
) -> ApiResponse[ReleaseReservationOut]:
    """Release the reservation for longrun job."""
    reservation_amount = await release.release_longrun_reservation(repos, job_id=job_id)
    return ApiResponse[ReleaseReservationOut](
        message="Longrun reservation has been released",
        data=ReleaseReservationOut(
            job_id=job_id,
            amount=reservation_amount,
        ),
    )
