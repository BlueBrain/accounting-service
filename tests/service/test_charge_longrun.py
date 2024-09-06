from decimal import Decimal

import pytest
from asyncpg.pgproto.pgproto import timedelta

from app.constants import TransactionType
from app.repository.group import RepositoryGroup
from app.schema.domain import ChargeLongrunResult
from app.service import charge_longrun as test_module
from app.utils import create_uuid, utcnow

from tests.constants import UUIDS
from tests.utils import _insert_longrun_job, _select_job, _select_ledger_rows, _update_job


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_longrun(db):
    repos = RepositoryGroup(db)
    now = utcnow()

    # no jobs
    result = await test_module.charge_longrun(repos, transaction_datetime=now)
    assert result == ChargeLongrunResult()

    # new job
    job_id = create_uuid()
    await _insert_longrun_job(db, job_id, instances=1, started_at=now - timedelta(minutes=10))

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    # unfinished_uncharged job
    transaction_datetime = now - timedelta(minutes=5)
    result = await test_module.charge_longrun(repos, transaction_datetime=transaction_datetime)
    assert result == ChargeLongrunResult(
        unfinished_uncharged=1,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2
    expected_amount = 300 * Decimal("0.01") + Decimal("1.5")
    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "unfinished_uncharged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "unfinished_uncharged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
    ]

    # unfinished_charged job
    transaction_datetime = now - timedelta(minutes=4)
    result = await test_module.charge_longrun(repos, transaction_datetime=transaction_datetime)
    assert result == ChargeLongrunResult(
        unfinished_charged=1,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 4
    expected_amount = 60 * Decimal("0.01")
    assert [dict(row._mapping) for row in rows[-2:]] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "unfinished_charged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "unfinished_charged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
    ]

    # finished_charged job
    now = utcnow()
    job = await _update_job(db, job_id, finished_at=now)
    assert job.finished_at == now

    transaction_datetime = now
    result = await test_module.charge_longrun(repos, transaction_datetime=transaction_datetime)
    assert result == ChargeLongrunResult(
        finished_charged=1,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 6
    expected_amount = 240 * Decimal("0.01")
    assert [dict(row._mapping) for row in rows[-2:]] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "finished_charged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "finished_charged:charge_project"},
            "transaction_datetime": transaction_datetime,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
    ]


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_longrun_expired_uncharged(db):
    repos = RepositoryGroup(db)

    job_id = create_uuid()
    now = utcnow()
    await _insert_longrun_job(db, job_id, instances=1, started_at=now - timedelta(hours=1))

    job = await _select_job(db, job_id)
    assert job.last_charged_at is None

    result = await test_module.charge_longrun(
        repos, expiration_interval=1800, transaction_datetime=now
    )
    assert result == ChargeLongrunResult(
        expired_uncharged=1,
    )
    job = await _select_job(db, job_id)
    assert job.last_charged_at == now
    assert job.finished_at == now
    assert job.cancelled_at == now
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2
    expected_amount = 3600 * Decimal("0.01") + Decimal("1.5")
    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "expired_uncharged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "expired_uncharged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
    ]


@pytest.mark.usefixtures("_db_account", "_db_price")
async def test_charge_longrun_expired_charged(db):
    repos = RepositoryGroup(db)

    job_id = create_uuid()
    now = utcnow()
    await _insert_longrun_job(
        db,
        job_id,
        instances=1,
        started_at=now - timedelta(minutes=70),
        last_charged_at=now - timedelta(minutes=60),
    )

    job = await _select_job(db, job_id)
    assert job.last_charged_at is not None

    result = await test_module.charge_longrun(
        repos, expiration_interval=1800, transaction_datetime=now
    )
    assert result == ChargeLongrunResult(
        expired_charged=1,
    )
    expected_amount = 3600 * Decimal("0.01")
    job = await _select_job(db, job_id)
    assert job.last_charged_at == now
    assert job.finished_at == now
    assert job.cancelled_at == now
    rows = await _select_ledger_rows(db, job_id)
    assert len(rows) == 2

    assert [dict(row._mapping) for row in rows] == [
        {
            "account_id": UUIDS.PROJ[0],
            "amount": -expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "expired_charged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
        {
            "account_id": UUIDS.SYS,
            "amount": expected_amount,
            "job_id": job_id,
            "price_id": 2,
            "properties": {"reason": "expired_charged:charge_project"},
            "transaction_datetime": now,
            "transaction_type": TransactionType.CHARGE_LONGRUN,
        },
    ]
