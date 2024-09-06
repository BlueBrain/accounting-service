from decimal import Decimal

import pytest
from asyncpg.pgproto.pgproto import timedelta

from app.constants import TransactionType
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeStorageResult
from app.service import charge_storage as test_module
from app.utils import create_uuid, utcnow

from tests.constants import GB, UUIDS
from tests.utils import _insert_storage_job, _select_job, _select_ledger_rows, _update_job


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_storage(db):
    repos = RepositoryGroup(db)
    now = utcnow()

    # no jobs
    result = await test_module.charge_storage(repos, jobs=[])
    assert result == ChargeStorageResult()

    # new job
    job_id = create_uuid()
    await _insert_storage_job(db, job_id, size=1 * GB, started_at=now - timedelta(minutes=120))

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    transaction_datetime = now - timedelta(minutes=60)
    result = await test_module.charge_storage(
        repos, jobs=[job], transaction_datetime=transaction_datetime
    )
    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at == transaction_datetime
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2
    expected_amount = 1 * GB * Decimal("0.001") * 3600
    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
    ]

    # running job
    transaction_datetime = now - timedelta(minutes=30)
    result = await test_module.charge_storage(
        repos, jobs=[job], transaction_datetime=transaction_datetime
    )

    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at == transaction_datetime
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 4
    expected_amount = 1 * GB * Decimal("0.001") * 1800
    assert [dict(row._mapping) for row in rows[-2:]] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
    ]

    # finished job
    finished_at = now - timedelta(minutes=20)
    job = await _update_job(db, job_id, finished_at=finished_at)

    transaction_datetime = now - timedelta(minutes=10)
    result = await test_module.charge_storage(
        repos, jobs=[job], transaction_datetime=transaction_datetime
    )

    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at == finished_at
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 6
    expected_amount = 1 * GB * Decimal("0.001") * 600
    assert [dict(row._mapping) for row in rows[-2:]] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
    ]

    # new job
    job_id = create_uuid()
    await _insert_storage_job(db, job_id, size=1.5 * GB, started_at=now - timedelta(minutes=20))

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    transaction_datetime = now - timedelta(minutes=10)
    result = await test_module.charge_storage(
        repos, jobs=[job], transaction_datetime=transaction_datetime
    )
    assert result == ChargeStorageResult(success=1)
    job = await _select_job(db, job_id)
    assert job.last_charged_at == transaction_datetime
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2
    expected_amount = int(1.5 * GB) * Decimal("0.001") * 600
    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 3,
            "properties": None,
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_STORAGE,
        },
    ]
