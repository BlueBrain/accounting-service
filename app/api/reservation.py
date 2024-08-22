"""Reservation api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    ApiResponse,
    MakeLongrunReservationIn,
    MakeOneshotReservationIn,
    MakeReservationOut,
    ReleaseReservationIn,
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
    return ApiResponse(
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
    return ApiResponse(
        message="Longrun reservation executed",
        data=result,
    )


@router.post("/oneshot/release")
async def release_oneshot_reservation(
    repos: RepoGroupDep,
    release_request: ReleaseReservationIn,
) -> ApiResponse[ReleaseReservationOut]:
    """Release the reservation for oneshot job."""
    reservation_amount = await release.release_oneshot_reservation(
        repos, proj_id=release_request.proj_id, job_id=release_request.job_id
    )
    return ApiResponse(
        message="Oneshot reservation has been released",
        data=ReleaseReservationOut(
            job_id=release_request.job_id,
            amount=reservation_amount,
        ),
    )


@router.post("/longrun/release")
async def release_longrun_reservation(
    repos: RepoGroupDep,
    release_request: ReleaseReservationIn,
) -> ApiResponse[ReleaseReservationOut]:
    """Release the reservation for longrun job."""
    reservation_amount = await release.release_longrun_reservation(
        repos, proj_id=release_request.proj_id, job_id=release_request.job_id
    )
    return ApiResponse(
        message="Longrun reservation has been released",
        data=ReleaseReservationOut(
            job_id=release_request.job_id,
            amount=reservation_amount,
        ),
    )
