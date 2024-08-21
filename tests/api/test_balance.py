import pytest

from tests.constants import PROJ_ID, PROJ_ID_2, VLAB_ID


@pytest.mark.usefixtures("_db_account")
async def test_get_balance_for_system(api_client):
    response = await api_client.get("/balance/system")

    assert response.json()["data"] == {"balance": "-3000.00"}
    assert response.status_code == 200


@pytest.mark.usefixtures("_db_account")
async def test_get_balance_for_virtual_lab(api_client):
    response = await api_client.get(f"/balance/virtual-lab/{VLAB_ID}")

    assert response.json()["data"] == {
        "vlab_id": VLAB_ID,
        "balance": "2000.00",
    }
    assert response.status_code == 200

    response = await api_client.get(
        f"/balance/virtual-lab/{VLAB_ID}",
        params={"include_projects": True},
    )

    assert response.json()["data"] == {
        "vlab_id": VLAB_ID,
        "balance": "2000.00",
        "projects": [
            {
                "balance": "400.00",
                "proj_id": PROJ_ID,
                "reservation": "100.00",
            },
            {
                "balance": "500.00",
                "proj_id": PROJ_ID_2,
                "reservation": "0.00",
            },
        ],
    }
    assert response.status_code == 200


@pytest.mark.usefixtures("_db_account")
async def test_get_balance_for_project(api_client):
    response = await api_client.get(f"/balance/project/{PROJ_ID}")

    assert response.json()["data"] == {
        "balance": "400.00",
        "proj_id": PROJ_ID,
        "reservation": "100.00",
    }
    assert response.status_code == 200
