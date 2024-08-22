import pytest
import sqlalchemy as sa

from app.constants import ServiceSubtype, ServiceType
from app.db.model import Job, Journal, Ledger
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeStorageResult, StartedJob
from app.service import charge_storage as test_module
from app.utils import create_uuid, utcnow

from tests.constants import GB, PROJ_ID, VLAB_ID


async def _insert_job(db, job_id, size, started_at):
    await db.execute(
        sa.insert(Job),
        [
            {
                "id": job_id,
                "vlab_id": VLAB_ID,
                "proj_id": PROJ_ID,
                "service_type": ServiceType.STORAGE,
                "service_subtype": ServiceSubtype.STORAGE,
                "started_at": started_at,
                "last_alive_at": started_at,
                "last_charged_at": None,
                "finished_at": None,
                "cancelled_at": None,
                "usage_params": {"size": int(size)},
            }
        ],
    )


async def _select_job(db, job_id):
    job = (await db.execute(sa.select(Job).where(Job.id == job_id))).scalar_one_or_none()
    return StartedJob.model_validate(job)


async def _select_ledger_rows(db, job_id):
    return (
        await db.execute(
            sa.select(Journal, Ledger).join_from(Journal, Ledger).where(Journal.job_id == job_id)
        )
    ).all()


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_storage(db):
    repos = RepositoryGroup(db)

    # no jobs
    result = await test_module.charge_storage(repos, jobs=[])

    # new job
    job_id = create_uuid()
    now = utcnow()
    await _insert_job(db, job_id, size=1 * GB, started_at=now)

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    result = await test_module.charge_storage(repos, jobs=[job])
    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    # running job
    result = await test_module.charge_storage(repos, jobs=[job])
    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 4

    # transitioning job
    job_id = create_uuid()
    now = utcnow()
    await _insert_job(db, job_id, size=1.5 * GB, started_at=now)

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    result = await test_module.charge_storage(repos, jobs=[job])
    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    # TODO: verify the content of the ledger rows
