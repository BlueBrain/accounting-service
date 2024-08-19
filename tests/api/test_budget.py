import pytest

from tests.constants import PROJ_ID, PROJ_ID_2, VLAB_ID


@pytest.mark.usefixtures("_db_account")
async def test_budget(api_client):
    response = await api_client.post(
        "/budget/top-up",
        json={"vlab_id": VLAB_ID, "amount": "123.45"},
    )

    assert response.json() == {}
    assert response.status_code == 200

    response = await api_client.post(
        "/budget/assign",
        json={"vlab_id": VLAB_ID, "proj_id": PROJ_ID, "amount": "23.45"},
    )

    assert response.json() == {}
    assert response.status_code == 200

    response = await api_client.post(
        "/budget/reverse",
        json={"vlab_id": VLAB_ID, "proj_id": PROJ_ID, "amount": "3.45"},
    )

    assert response.json() == {}
    assert response.status_code == 200

    response = await api_client.post(
        "/budget/move",
        json={
            "vlab_id": VLAB_ID,
            "debited_from": PROJ_ID,
            "credited_to": PROJ_ID_2,
            "amount": "20.00",
        },
    )

    assert response.json() == {}
    assert response.status_code == 200

    # TODO: verify the content of the ledger and account rows
