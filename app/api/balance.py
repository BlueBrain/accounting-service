"""Balance api."""

from uuid import UUID

from fastapi import APIRouter

from app.dependencies import RepoGroupDep
from app.schema.api import ApiResponse, ProjBalanceOut, SysBalanceOut, VlabBalanceOut
from app.service import balance as balance_service

router = APIRouter()


@router.get("/system")
async def get_balance_for_system(repos: RepoGroupDep) -> ApiResponse[SysBalanceOut]:
    """Return the balance for thr system."""
    result = await balance_service.get_balance_for_system(repos)
    return ApiResponse(
        message="Balance for system",
        data=result,
    )


@router.get("/virtual-lab/{vlab_id}", response_model_exclude_defaults=True)
async def get_balance_for_virtual_lab(
    repos: RepoGroupDep, *, vlab_id: UUID, include_projects: bool = False
) -> ApiResponse[VlabBalanceOut]:
    """Return the balance for a given virtual-lab."""
    result = await balance_service.get_balance_for_vlab(
        repos, vlab_id=vlab_id, include_projects=include_projects
    )
    return ApiResponse(
        message=f"Balance for virtual-lab{' including projects' if include_projects else ''}",
        data=result,
    )


@router.get("/project/{proj_id}")
async def get_balance_for_project(
    repos: RepoGroupDep, proj_id: UUID
) -> ApiResponse[ProjBalanceOut]:
    """Return the balance for a given project."""
    result = await balance_service.get_balance_for_project(repos, proj_id=proj_id)
    return ApiResponse(
        message="Balance for project",
        data=result,
    )
