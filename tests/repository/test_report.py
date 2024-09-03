from decimal import Decimal
from unittest.mock import ANY

import pytest

from app.constants import D0, ServiceSubtype, ServiceType
from app.repository import report as test_module
from app.schema.api import PaginatedParams

from tests.constants import PROJ_ID, UUIDS, VLAB_ID

EXPECTED = [
    {
        "job_id": UUIDS.JOB[0],
        "type": ServiceType.ONESHOT,
        "subtype": ServiceSubtype.ML_LLM,
        "reserved_at": ANY,
        "started_at": ANY,
        "finished_at": ANY,
        "cancelled_at": None,
        "amount": Decimal("0.015"),
        "reserved_amount": Decimal("0.010"),
        "count": 1500,
        "reserved_count": 1000,
        "duration": None,
        "reserved_duration": None,
        "size": None,
    },
    {
        "job_id": UUIDS.JOB[1],
        "type": ServiceType.LONGRUN,
        "subtype": ServiceSubtype.SINGLE_CELL_SIM,
        "reserved_at": ANY,
        "started_at": ANY,
        "finished_at": ANY,
        "cancelled_at": None,
        "amount": D0,  # no ledger records
        "reserved_amount": D0,  # no ledger records
        "count": None,
        "reserved_count": None,
        "duration": 90,
        "reserved_duration": 60,
        "size": None,
    },
    {
        "job_id": UUIDS.JOB[2],
        "type": ServiceType.STORAGE,
        "subtype": ServiceSubtype.STORAGE,
        "reserved_at": None,
        "started_at": ANY,
        "finished_at": ANY,
        "cancelled_at": None,
        "amount": D0,  # no ledger records
        "reserved_amount": D0,  # no ledger records
        "count": None,
        "reserved_count": None,
        "duration": 120,
        "reserved_duration": None,
        "size": 1000,
    },
]


@pytest.mark.usefixtures("_db_ledger")
async def test_get_job_reports(db):
    repo = test_module.ReportRepository(db)

    started_after = None
    started_before = None

    page = 1
    page_size = 3
    pagination = PaginatedParams(page=page, page_size=page_size)

    result, count = await repo.get_job_reports(
        pagination=pagination,
        vlab_id=VLAB_ID,
        proj_id=PROJ_ID,
        started_after=started_after,
        started_before=started_before,
    )

    assert count == 3
    assert len(result) == page_size
    assert [dict(row._mapping) for row in result] == EXPECTED

    for page in 1, 2, 3:
        for page_size in 1, 2, 3:
            pagination = PaginatedParams(page=page, page_size=page_size)

            result, count = await repo.get_job_reports(
                pagination=pagination,
                vlab_id=VLAB_ID,
                proj_id=PROJ_ID,
                started_after=started_after,
                started_before=started_before,
            )

            assert count == 3
            assert [dict(row._mapping) for row in result] == EXPECTED[
                page_size * (page - 1) : page_size * page
            ]
