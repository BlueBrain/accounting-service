"""Report api."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from starlette.requests import Request

from app.dependencies import RepoGroupDep
from app.schema.api import ApiResponse, JobReportUnionOut, PaginatedOut, PaginatedParams
from app.service import report as report_service

router = APIRouter()


@router.get("/system", response_model_exclude_defaults=True)
async def get_jobs_for_system(
    request: Request,
    repos: RepoGroupDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1)] = 1000,
) -> ApiResponse[PaginatedOut[JobReportUnionOut]]:
    """Return the job report for a given virtual-lab."""
    pagination = PaginatedParams(page=page, page_size=page_size)
    jobs, total_items = await report_service.get_report_for_system(repos, pagination=pagination)
    result = PaginatedOut[JobReportUnionOut].new(
        items=jobs, total_items=total_items, pagination=pagination, url=request.url
    )
    return ApiResponse(
        message="Job report for system",
        data=result,
    )


@router.get("/virtual-lab/{vlab_id}", response_model_exclude_defaults=True)
async def get_jobs_for_vlab(
    request: Request,
    repos: RepoGroupDep,
    vlab_id: UUID,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1)] = 1000,
) -> ApiResponse[PaginatedOut[JobReportUnionOut]]:
    """Return the job report for a given virtual-lab."""
    pagination = PaginatedParams(page=page, page_size=page_size)
    jobs, total_items = await report_service.get_report_for_vlab(
        repos, vlab_id=vlab_id, pagination=pagination
    )
    result = PaginatedOut[JobReportUnionOut].new(
        items=jobs, total_items=total_items, pagination=pagination, url=request.url
    )
    return ApiResponse(
        message=f"Job report for virtual-lab {vlab_id}",
        data=result,
    )


@router.get("/project/{proj_id}", response_model_exclude_defaults=True)
async def get_jobs_for_proj(
    request: Request,
    repos: RepoGroupDep,
    proj_id: UUID,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1)] = 1000,
) -> ApiResponse[PaginatedOut[JobReportUnionOut]]:
    """Return the job report for a given project."""
    pagination = PaginatedParams(page=page, page_size=page_size)
    jobs, total_items = await report_service.get_report_for_project(
        repos, proj_id=proj_id, pagination=pagination
    )
    result = PaginatedOut[JobReportUnionOut].new(
        items=jobs, total_items=total_items, pagination=pagination, url=request.url
    )
    return ApiResponse(
        message=f"Job report for project {proj_id}",
        data=result,
    )
