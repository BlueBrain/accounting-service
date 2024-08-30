"""Report api."""

from uuid import UUID

from fastapi import APIRouter

from app.dependencies import RepoGroupDep
from app.schema.api import ApiResponse, ProjReportOut, VlabReportOut
from app.service import report as report_service

router = APIRouter()


@router.get("/virtual-lab/{vlab_id}")
async def get_jobs_for_vlab(repos: RepoGroupDep, vlab_id: UUID) -> ApiResponse[VlabReportOut]:
    """Return the job report for a given virtual-lab."""
    result = await report_service.get_report_for_vlab(repos, vlab_id=vlab_id)
    return ApiResponse(
        message="Job report for virtual-lab",
        data=result,
    )


@router.get("/project/{proj_id}")
async def get_jobs_for_proj(repos: RepoGroupDep, proj_id: UUID) -> ApiResponse[ProjReportOut]:
    """Return the job report for a given project."""
    result = await report_service.get_report_for_project(repos, proj_id=proj_id)
    return ApiResponse(
        message="Job report for project",
        data=result,
    )
