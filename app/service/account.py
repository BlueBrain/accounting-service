"""Account service."""

from uuid import UUID

from app.repository.group import RepositoryGroup
from app.schema.domain import ProjAccount, SysAccount, VlabAccount


async def add_system(repos: RepositoryGroup, account_id: UUID, name: str) -> SysAccount:
    """Add the system account."""
    return await repos.account.add_sys_account(account_id=account_id, name=name)


async def add_virtual_lab(repos: RepositoryGroup, account_id: UUID, name: str) -> VlabAccount:
    """Add a new virtual lab account."""
    return await repos.account.add_vlab_account(account_id=account_id, name=name)


async def add_project(
    repos: RepositoryGroup, account_id: UUID, name: str, vlab_id: UUID
) -> ProjAccount:
    """Add a new project account."""
    return await repos.account.add_proj_account(account_id=account_id, name=name, vlab_id=vlab_id)
