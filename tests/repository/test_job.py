from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.constants import ServiceSubtype, ServiceType
from app.db.model import Job
from app.repository import job as test_module

from tests.constants import PROJ_ID, VLAB_ID


@pytest.mark.usefixtures("_db_account")
async def test_insert_job(db):
    repo = test_module.JobRepository(db)
    started_at = datetime.fromtimestamp(1719325921.883, tz=UTC)
    result = await repo.insert_job(
        job_id=UUID("e0f0cd3c-595a-47a7-b292-267124f5a8df"),
        vlab_id=UUID(VLAB_ID),
        proj_id=UUID(PROJ_ID),
        service_type=ServiceType.STORAGE,
        service_subtype=ServiceSubtype.STORAGE,
        started_at=started_at,
        finished_at=None,
        usage_params={"size": 1073741824},
    )

    assert isinstance(result, Job)
    assert result.id is not None
