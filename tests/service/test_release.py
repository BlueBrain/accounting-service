from decimal import Decimal

import pytest
import sqlalchemy as sa

from app.constants import ServiceSubtype, ServiceType, TransactionType
from app.db.model import Account
from app.errors import ApiError, ApiErrorCode
from app.repository.group import RepositoryGroup
from app.service import release as test_module
from app.utils import utcnow

from tests.constants import UUIDS


async def _get_balances(db):
    proj_balance = (
        (await db.execute(sa.select(Account).where(Account.id == UUIDS.PROJ[0])))
        .scalar_one()
        .balance
    )
    rsv_balance = (
        (await db.execute(sa.select(Account).where(Account.id == UUIDS.RSV[0])))
        .scalar_one()
        .balance
    )
    return proj_balance, rsv_balance


async def _test_release(db, test_func, service_type, service_subtype):
    repos = RepositoryGroup(db)
    now = utcnow()
    amount = Decimal("12.34")
    count = 1000

    # no jobs
    with pytest.raises(ApiError, match="The specified job cannot be found") as exc_info:
        await test_func(repos, job_id=UUIDS.JOB[0])
    assert exc_info.value.error_code == ApiErrorCode.ENTITY_NOT_FOUND

    proj_balance_initial, rsv_balance_initial = await _get_balances(db)

    # new job
    await repos.job.insert_job(
        job_id=UUIDS.JOB[0],
        vlab_id=UUIDS.VLAB[0],
        proj_id=UUIDS.PROJ[0],
        service_type=service_type,
        service_subtype=service_subtype,
        reserved_at=now,
        reservation_params={"count": int(count)},
    )
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=UUIDS.PROJ[0],
        credited_to=UUIDS.RSV[0],
        transaction_datetime=now,
        transaction_type=TransactionType.RESERVE,
        job_id=UUIDS.JOB[0],
    )

    proj_balance_before, rsv_balance_before = await _get_balances(db)
    assert proj_balance_before == proj_balance_initial - amount
    assert rsv_balance_before == rsv_balance_initial + amount

    result = await test_func(repos, job_id=UUIDS.JOB[0])
    assert result == amount

    proj_balance_after, rsv_balance_after = await _get_balances(db)
    assert rsv_balance_after == rsv_balance_initial
    assert proj_balance_after == proj_balance_initial


@pytest.mark.usefixtures("_db_account")
async def test_release_oneshot(db):
    await _test_release(
        db,
        test_func=test_module.release_oneshot_reservation,
        service_type=ServiceType.ONESHOT,
        service_subtype=ServiceSubtype.ML_LLM,
    )


@pytest.mark.usefixtures("_db_account")
async def test_release_longrun(db):
    await _test_release(
        db,
        test_func=test_module.release_longrun_reservation,
        service_type=ServiceType.LONGRUN,
        service_subtype=ServiceSubtype.SINGLE_CELL_SIM,
    )
