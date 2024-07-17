import pytest
import sqlalchemy as sa

from app.constants import ServiceType
from app.db.model import Job, Journal, Ledger
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeLongJobsResult
from app.service import charge_long_jobs as test_module
from app.utils import create_uuid, utcnow

from tests.constants import PROJ_ID, VLAB_ID


async def _insert_job(db, job_id, units, started_at):
    await db.execute(
        sa.insert(Job).values(
            [
                {
                    "id": job_id,
                    "vlab_id": VLAB_ID,
                    "proj_id": PROJ_ID,
                    "service_type": ServiceType.LONG_JOBS,
                    "units": int(units),
                    "started_at": started_at,
                    "last_alive_at": started_at,
                    "last_charged_at": None,
                    "finished_at": None,
                    "cancelled_at": None,
                }
            ],
        )
    )


async def _update_job(db, job_id, **kwargs):
    return (
        await db.execute(sa.update(Job).values(**kwargs).where(Job.id == job_id).returning(Job))
    ).scalar_one()


async def _select_job(db, job_id):
    return (await db.execute(sa.select(Job).where(Job.id == job_id))).scalar_one_or_none()


async def _select_ledger_rows(db, job_id):
    return (
        await db.execute(
            sa.select(Journal, Ledger).join_from(Journal, Ledger).where(Journal.job_id == job_id)
        )
    ).all()


@pytest.mark.usefixtures("_db_account")
async def test_charge_long_jobs(db):
    repos = RepositoryGroup(db)

    # no jobs
    result = await test_module.charge_long_jobs(repos)
    assert result == ChargeLongJobsResult(
        unfinished_uncharged=0,
        unfinished_charged=0,
        finished_uncharged=0,
        finished_charged=0,
        finished_overcharged=0,
    )

    # new job
    job_id = create_uuid()
    now = utcnow()
    await _insert_job(db, job_id, units=0, started_at=now)

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    result = await test_module.charge_long_jobs(repos)
    assert result == ChargeLongJobsResult(
        unfinished_uncharged=1,
        unfinished_charged=0,
        finished_uncharged=0,
        finished_charged=0,
        finished_overcharged=0,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    # unfinished_charged job
    result = await test_module.charge_long_jobs(repos)
    assert result == ChargeLongJobsResult(
        unfinished_uncharged=0,
        unfinished_charged=1,
        finished_uncharged=0,
        finished_charged=0,
        finished_overcharged=0,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    # finished_charged job
    now = utcnow()
    job = await _update_job(db, job_id, finished_at=now)
    assert job.finished_at == now

    result = await test_module.charge_long_jobs(repos)
    assert result == ChargeLongJobsResult(
        unfinished_uncharged=0,
        unfinished_charged=0,
        finished_uncharged=0,
        finished_charged=1,
        finished_overcharged=0,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    # TODO: verify the content of the ledger rows
