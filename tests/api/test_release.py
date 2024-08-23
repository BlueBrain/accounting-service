from decimal import Decimal
from unittest.mock import create_autospec

from app.service import release

from tests.constants import UUIDS


async def test_release_oneshot_reservation(api_client, monkeypatch):
    job_id = str(UUIDS.JOB[0])
    amount = Decimal("12.34")
    m = create_autospec(release.release_oneshot_reservation, return_value=amount)
    monkeypatch.setattr(release, "release_oneshot_reservation", m)
    response = await api_client.delete(f"/reservation/oneshot/{job_id}")

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "job_id": str(UUIDS.JOB[0]),
        "amount": str(amount),
    }
    assert m.call_count == 1


async def test_release_longrun_reservation(api_client, monkeypatch):
    job_id = str(UUIDS.JOB[0])
    amount = Decimal("12.34")
    m = create_autospec(release.release_longrun_reservation, return_value=amount)
    monkeypatch.setattr(release, "release_longrun_reservation", m)
    response = await api_client.delete(f"/reservation/longrun/{job_id}")

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "job_id": str(UUIDS.JOB[0]),
        "amount": str(amount),
    }
    assert m.call_count == 1
