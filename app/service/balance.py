"""Balance service."""

from uuid import UUID

from app.errors import ensure_result
from app.repository.group import RepositoryGroup
from app.schema.api import ProjBalanceOut, SysBalanceOut, VlabBalanceOut
from app.schema.domain import ProjAccount


async def _get_balance_for_projects(
    repos: RepositoryGroup, project_accounts: list[ProjAccount]
) -> list[ProjBalanceOut]:
    if not project_accounts:
        return []
    reservation_accounts = await repos.account.get_reservation_accounts(
        proj_ids=[proj.id for proj in project_accounts]
    )
    reservation_dict = {
        reservation.proj_id: reservation.balance for reservation in reservation_accounts
    }
    return [
        ProjBalanceOut(
            proj_id=project.id,
            balance=project.balance,
            reservation=reservation_dict[project.id],
        )
        for project in project_accounts
    ]


async def get_balance_for_project(repos: RepositoryGroup, proj_id: UUID) -> ProjBalanceOut:
    """Return the balance for a given project, including the reserved amount."""
    with ensure_result(error_message="Project not found"):
        project_account = await repos.account.get_proj_account(proj_id=proj_id)
    projects = await _get_balance_for_projects(repos, project_accounts=[project_account])
    return projects[0]


async def get_balance_for_vlab(
    repos: RepositoryGroup, vlab_id: UUID, *, include_projects: bool = False
) -> VlabBalanceOut:
    """Return the balance for a given virtual-lab."""
    with ensure_result(error_message="Virtual lab not found"):
        vlab = await repos.account.get_vlab_account(vlab_id=vlab_id)
    projects = None
    if include_projects:
        project_accounts = await repos.account.get_proj_accounts_for_vlab(vlab_id=vlab_id)
        projects = await _get_balance_for_projects(repos, project_accounts=project_accounts)
    return VlabBalanceOut(
        vlab_id=vlab_id,
        balance=vlab.balance,
        projects=projects,
    )


async def get_balance_for_system(repos: RepositoryGroup) -> SysBalanceOut:
    """Return the balance for the system account."""
    with ensure_result(error_message="System account not found"):
        sys = await repos.account.get_system_account()
    return SysBalanceOut(
        balance=sys.balance,
    )
