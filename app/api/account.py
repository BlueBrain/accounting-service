"""Account api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import (
    ApiResponse,
    ProjAccountCreationIn,
    ProjAccountCreationOut,
    SysAccountCreationIn,
    SysAccountCreationOut,
    VlabAccountCreationIn,
    VlabAccountCreationOut,
)
from app.service import account as account_service

router = APIRouter()


@router.post("/system", status_code=status.HTTP_201_CREATED)
async def add_system_account(
    repos: RepoGroupDep, account: SysAccountCreationIn
) -> ApiResponse[SysAccountCreationOut]:
    """Add the system account."""
    result = await account_service.add_system(repos, account_id=account.id, name=account.name)
    return ApiResponse[SysAccountCreationOut](
        message="System account created",
        data=SysAccountCreationOut.model_validate(result, from_attributes=True),
    )


@router.post("/virtual-lab", status_code=status.HTTP_201_CREATED)
async def add_virtual_lab_account(
    repos: RepoGroupDep, account: VlabAccountCreationIn
) -> ApiResponse[VlabAccountCreationOut]:
    """Add a new virtual lab account."""
    result = await account_service.add_virtual_lab(repos, account_id=account.id, name=account.name)
    return ApiResponse[VlabAccountCreationOut](
        message="Virtual lab created",
        data=VlabAccountCreationOut.model_validate(result, from_attributes=True),
    )


@router.post("/project", status_code=status.HTTP_201_CREATED)
async def add_project_account(
    repos: RepoGroupDep, account: ProjAccountCreationIn
) -> ApiResponse[ProjAccountCreationOut]:
    """Add a new project account."""
    result = await account_service.add_project(
        repos, account_id=account.id, name=account.name, vlab_id=account.vlab_id
    )
    return ApiResponse[ProjAccountCreationOut](
        message="Project created",
        data=ProjAccountCreationOut.model_validate(result, from_attributes=True),
    )
