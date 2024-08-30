"""Report service."""

from uuid import UUID

from app.errors import ensure_result
from app.repository.group import RepositoryGroup
from app.schema.api import ProjReportOut, VlabReportOut
from app.schema.domain import ProjAccount


async def _get_report_for_projects(
    repos: RepositoryGroup, project_accounts: list[ProjAccount]
) -> list[ProjReportOut]:
    result = []
    for project in project_accounts:
        jobs = await repos.report.get_job_reports(proj_id=project.id)
        item = ProjReportOut.model_validate({"proj_id": project.id, "jobs": jobs})
        result.append(item)
    return result


async def get_report_for_project(repos: RepositoryGroup, proj_id: UUID) -> ProjReportOut:
    """Return the job report for a given project, including the reserved amount."""
    with ensure_result(error_message="Project not found"):
        project_account = await repos.account.get_proj_account(proj_id=proj_id)
    projects = await _get_report_for_projects(repos, project_accounts=[project_account])
    return projects[0]


async def get_report_for_vlab(repos: RepositoryGroup, vlab_id: UUID) -> VlabReportOut:
    """Return the job report for a given virtual-lab."""
    with ensure_result(error_message="Virtual lab not found"):
        await repos.account.get_vlab_account(vlab_id=vlab_id)
    project_accounts = await repos.account.get_proj_accounts_for_vlab(vlab_id=vlab_id)
    projects = await _get_report_for_projects(repos, project_accounts=project_accounts)
    return VlabReportOut.model_validate({"vlab_id": vlab_id, "projects": projects})
