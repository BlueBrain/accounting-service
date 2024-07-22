"""Account api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    ProjAccountCreationRequest,
    ProjAccountCreationResponse,
    SysAccountCreationRequest,
    SysAccountCreationResponse,
    VlabAccountCreationRequest,
    VlabAccountCreationResponse,
)
from app.service import account as account_service

router = APIRouter()


@router.post("/system", status_code=status.HTTP_201_CREATED)
async def add_system_account(
    repos: RepoGroupDep, account: SysAccountCreationRequest
) -> SysAccountCreationResponse:
    """Add the system account."""
    result = await account_service.add_system(repos, account_id=account.id, name=account.name)
    return SysAccountCreationResponse.model_validate(result, from_attributes=True)


@router.post("/virtual-lab", status_code=status.HTTP_201_CREATED)
async def add_virtual_lab_account(
    repos: RepoGroupDep, account: VlabAccountCreationRequest
) -> VlabAccountCreationResponse:
    """Add a new virtual lab account."""
    result = await account_service.add_virtual_lab(repos, account_id=account.id, name=account.name)
    return VlabAccountCreationResponse.model_validate(result, from_attributes=True)


@router.post("/project", status_code=status.HTTP_201_CREATED)
async def add_project_account(
    repos: RepoGroupDep, account: ProjAccountCreationRequest
) -> ProjAccountCreationResponse:
    """Add a new project account."""
    result = await account_service.add_project(
        repos, account_id=account.id, name=account.name, vlab_id=account.vlab_id
    )
    return ProjAccountCreationResponse.model_validate(result, from_attributes=True)
