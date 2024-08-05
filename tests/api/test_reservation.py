import pytest

from app.constants import ServiceType

from tests.constants import PROJ_ID


@pytest.mark.usefixtures("_db_account")
async def test_make_oneshot_reservation(api_client, mock_uuid):
    # make a valid reservation
    request_payload = {
        "proj_id": PROJ_ID,
        "type": ServiceType.ONESHOT,
        "subtype": "ml_queries",
        "count": "1",
    }
    response = await api_client.post("/api/reservation/oneshot", json=request_payload)

    assert response.json() == {
        "job_id": "00000000-0000-0000-0000-000000000001",
        "is_allowed": True,
        "requested_amount": "10",
        "available_amount": "400",
    }
    assert response.status_code == 200
    assert mock_uuid.call_count == 1
    mock_uuid.reset_mock()

    # try to make a new reservation with insufficient funds because of the previous reservation
    request_payload = {
        "proj_id": PROJ_ID,
        "type": ServiceType.ONESHOT,
        "subtype": "ml_queries",
        "count": "40",
    }
    response = await api_client.post("/api/reservation/oneshot", json=request_payload)

    assert response.json() == {
        "job_id": None,
        "is_allowed": False,
        "requested_amount": "400",
        "available_amount": "390",
    }
    assert response.status_code == 200
    assert mock_uuid.call_count == 0


@pytest.mark.usefixtures("_db_account")
async def test_make_longrun_reservation(api_client, mock_uuid):
    # make a valid reservation
    request_payload = {
        "proj_id": PROJ_ID,
        "type": ServiceType.LONGRUN,
        "subtype": "single_cell_sim",
        "instances": "1",
        "instance_type": "",
    }
    response = await api_client.post("/api/reservation/longrun", json=request_payload)

    assert response.json() == {
        "job_id": "00000000-0000-0000-0000-000000000001",
        "is_allowed": True,
        "requested_amount": "100",
        "available_amount": "400",
    }
    assert response.status_code == 200
    assert mock_uuid.call_count == 1
    mock_uuid.reset_mock()

    # try to make a new reservation with insufficient funds because of the previous reservation
    request_payload = {
        "proj_id": PROJ_ID,
        "type": ServiceType.LONGRUN,
        "subtype": "single_cell_sim",
        "instances": "4",
        "instance_type": "",
    }
    response = await api_client.post("/api/reservation/longrun", json=request_payload)

    assert response.json() == {
        "job_id": None,
        "is_allowed": False,
        "requested_amount": "400",
        "available_amount": "300",
    }
    assert response.status_code == 200
    assert mock_uuid.call_count == 0
