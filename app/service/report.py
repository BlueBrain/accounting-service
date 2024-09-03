"""Report service."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Row

from app.errors import ensure_result
from app.repository.group import RepositoryGroup
from app.schema.api import PaginatedParams


async def get_report_for_system(
    repos: RepositoryGroup, pagination: PaginatedParams
) -> tuple[Sequence[Row], int]:
    """Return the job report for the full system."""
    return await repos.report.get_job_reports(pagination=pagination)


async def get_report_for_vlab(
    repos: RepositoryGroup, vlab_id: UUID, pagination: PaginatedParams
) -> tuple[Sequence[Row], int]:
    """Return the job report for a given virtual-lab."""
    with ensure_result(error_message="Virtual lab not found"):
        vlab_account = await repos.account.get_vlab_account(vlab_id=vlab_id)
    return await repos.report.get_job_reports(pagination=pagination, vlab_id=vlab_account.id)


async def get_report_for_project(
    repos: RepositoryGroup, proj_id: UUID, pagination: PaginatedParams
) -> tuple[Sequence[Row], int]:
    """Return the job report for a given project, including the reserved amount."""
    with ensure_result(error_message="Project not found"):
        proj_account = await repos.account.get_proj_account(proj_id=proj_id)
    return await repos.report.get_job_reports(pagination=pagination, proj_id=proj_account.id)
