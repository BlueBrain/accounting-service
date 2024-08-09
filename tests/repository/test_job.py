from datetime import UTC, datetime
from uuid import UUID

from app.constants import ServiceSubtype, ServiceType
from app.db.model import Job
from app.repository import job as test_module


async def test_insert_job(db):
    repo = test_module.JobRepository(db)
    started_at = datetime.fromtimestamp(1719325921.883, tz=UTC)
    result = await repo.insert_job(
        job_id=UUID("e0f0cd3c-595a-47a7-b292-267124f5a8df"),
        vlab_id=UUID("43574586-739a-497d-9e93-532b54f1cb22"),
        proj_id=UUID("759bb837-4fac-46e8-9ea4-ed98c68c0fb9"),
        service_type=ServiceType.STORAGE,
        service_subtype=ServiceSubtype.STORAGE,
        started_at=started_at,
        finished_at=None,
        usage_params={"size": 1073741824},
    )

    assert isinstance(result, Job)
    assert result.id is not None
