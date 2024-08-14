import pytest

from app.constants import ServiceSubtype, ServiceType

from tests.constants import PROJ_ID, VLAB_ID


async def test_post_price(api_client):
    data = {
        "service_type": ServiceType.ONESHOT,
        "service_subtype": ServiceSubtype.ML_LLM,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": None,
        "fixed_cost": "0",
        "multiplier": "0.00001",
        "vlab_id": None,
    }
    response = await api_client.post("/api/price", json=data)

    assert response.json() == data | {"id": 1}
    assert response.status_code == 201


@pytest.mark.usefixtures("_db_account")
async def test_post_price_with_vlab_and_valid_to(api_client):
    data = {
        "service_type": ServiceType.ONESHOT,
        "service_subtype": ServiceSubtype.ML_LLM,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": "2034-01-01T00:00:00Z",
        "fixed_cost": "0",
        "multiplier": "0.00001",
        "vlab_id": VLAB_ID,
    }
    response = await api_client.post("/api/price", json=data)

    assert response.json() == data | {"id": 1}
    assert response.status_code == 201


@pytest.mark.usefixtures("_db_account")
async def test_post_price_with_proj_instead_of_vlab(api_client):
    data = {
        "service_type": ServiceType.ONESHOT,
        "service_subtype": ServiceSubtype.ML_LLM,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": None,
        "fixed_cost": "0",
        "multiplier": "0.00001",
        "vlab_id": PROJ_ID,
    }
    response = await api_client.post("/api/price", json=data)

    assert response.status_code == 404


async def test_post_price_with_invalid_valid_to(api_client):
    data = {
        "service_type": ServiceType.ONESHOT,
        "service_subtype": ServiceSubtype.ML_LLM,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": "2023-01-01T00:00:00Z",
        "fixed_cost": "0",
        "multiplier": "0.00001",
        "vlab_id": None,
    }
    response = await api_client.post("/api/price", json=data)

    assert response.status_code == 422


async def test_post_price_with_invalid_costs(api_client):
    data = {
        "service_type": ServiceType.ONESHOT,
        "service_subtype": ServiceSubtype.ML_LLM,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": None,
        "fixed_cost": "-1.0",
        "multiplier": "-0.00001",
        "vlab_id": None,
    }
    response = await api_client.post("/api/price", json=data)

    assert response.status_code == 422
