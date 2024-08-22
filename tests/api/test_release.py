from decimal import Decimal
from unittest.mock import create_autospec

from app.service import release

from tests.constants import UUIDS


async def test_release_oneshot_reservation(api_client, monkeypatch):
    amount = Decimal("12.34")
    m = create_autospec(release.release_oneshot_reservation, return_value=amount)
    monkeypatch.setattr(release, "release_oneshot_reservation", m)
    request_payload = {
        "proj_id": str(UUIDS.PROJ[0]),
        "job_id": str(UUIDS.JOB[0]),
    }
    response = await api_client.post("/reservation/oneshot/release", json=request_payload)

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "job_id": str(UUIDS.JOB[0]),
        "amount": str(amount),
    }
    assert m.call_count == 1


async def test_release_longrun_reservation(api_client, monkeypatch):
    amount = Decimal("12.34")
    m = create_autospec(release.release_longrun_reservation, return_value=amount)
    monkeypatch.setattr(release, "release_longrun_reservation", m)
    request_payload = {
        "proj_id": str(UUIDS.PROJ[0]),
        "job_id": str(UUIDS.JOB[0]),
    }
    response = await api_client.post("/reservation/longrun/release", json=request_payload)

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "job_id": str(UUIDS.JOB[0]),
        "amount": str(amount),
    }
    assert m.call_count == 1
