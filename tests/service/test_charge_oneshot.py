from decimal import Decimal

import pytest

from app.constants import TransactionType
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeOneshotResult
from app.service import charge_oneshot as test_module
from app.utils import create_uuid, utcnow

from tests.constants import UUIDS
from tests.utils import _insert_oneshot_job, _select_job, _select_ledger_rows, _update_job


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_oneshot(db):
    repos = RepositoryGroup(db)
    now = utcnow()

    # no jobs
    result = await test_module.charge_oneshot(repos)
    assert result == ChargeOneshotResult()
    # new job
    job_id = create_uuid()
    await _insert_oneshot_job(db, job_id, reserved_count=100, reserved_at=now)

    result = await test_module.charge_oneshot(repos)
    assert result == ChargeOneshotResult(success=0)

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    # finished job
    count = 150
    job = await _update_job(
        db,
        job_id,
        started_at=now,
        last_alive_at=now,
        finished_at=now,
        usage_params={"count": int(count)},
    )
    assert job.started_at == now
    assert job.finished_at == now

    result = await test_module.charge_oneshot(repos)
    assert result == ChargeOneshotResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2
    expected_amount = 150 * Decimal("0.00001")
    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 1,
            "properties": {"reason": "finished_uncharged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_ONESHOT,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 1,
            "properties": {"reason": "finished_uncharged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_ONESHOT,
        },
    ]
