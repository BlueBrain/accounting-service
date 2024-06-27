from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.constants import ServiceType
from app.db.models import Usage
from app.repositories import usage as test_module

pytestmark = pytest.mark.usefixtures("db_cleanup")


async def test_add_usage(db):
    repo = test_module.UsageRepository(db)
    started_at = datetime.fromtimestamp(1719325921.883, tz=UTC)
    result = await repo.add_usage(
        vlab_id=UUID("43574586-739a-497d-9e93-532b54f1cb22"),
        proj_id=UUID("759bb837-4fac-46e8-9ea4-ed98c68c0fb9"),
        job_id=None,
        service_type=ServiceType.STORAGE,
        service_subtype="",
        units=1234,
        started_at=started_at,
        finished_at=None,
        properties=None,
    )

    assert isinstance(result, Usage)
    assert result.id is not None
