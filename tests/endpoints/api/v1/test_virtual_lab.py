import pytest

pytestmark = pytest.mark.usefixtures("db_cleanup")


async def test_get_virtual_lab(api_client):
    uuid = "65ffe6ed-1c46-4a81-a595-000000000000"
    response = await api_client.get(f"/api/v1/virtual-lab/{uuid}")

    assert response.status_code == 200
    assert response.json() == {"virtual_lab_id": uuid}
