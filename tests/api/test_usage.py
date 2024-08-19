from unittest.mock import AsyncMock

import pytest

from app.constants import ServiceSubtype, ServiceType
from app.dependencies import _sqs_manager
from app.queue.session import SQSManager
from app.utils import since_unix_epoch

from tests.constants import PROJ_ID


@pytest.fixture
def mock_sqs_manager(app, monkeypatch):
    m = AsyncMock(SQSManager, client=AsyncMock())
    monkeypatch.setitem(app.dependency_overrides, _sqs_manager, lambda: m)
    return m


async def test_add_oneshot_usage(api_client, mock_sqs_manager):
    timestamp = since_unix_epoch()
    request_payload = {
        "job_id": "00000000-0000-0000-0000-000000000001",
        "proj_id": PROJ_ID,
        "type": ServiceType.ONESHOT,
        "subtype": ServiceSubtype.ML_LLM,
        "count": "1000000",
        "timestamp": timestamp,
    }
    response = await api_client.post("/usage/oneshot", json=request_payload)

    assert response.json() == {}
    assert response.status_code == 201
    assert mock_sqs_manager.client.send_message.await_count == 1


async def test_add_longrun_usage(api_client, mock_sqs_manager):
    timestamp = since_unix_epoch()
    request_payload = {
        "job_id": "00000000-0000-0000-0000-000000000001",
        "proj_id": PROJ_ID,
        "type": ServiceType.LONGRUN,
        "subtype": ServiceSubtype.SINGLE_CELL_SIM,
        "instances": "2",
        "instance_type": "",
        "status": "started",
        "timestamp": timestamp,
    }
    response = await api_client.post("/usage/longrun", json=request_payload)

    assert response.json() == {}
    assert response.status_code == 201
    assert mock_sqs_manager.client.send_message.await_count == 1


async def test_add_storage_usage(api_client, mock_sqs_manager):
    timestamp = since_unix_epoch()
    request_payload = {
        "proj_id": PROJ_ID,
        "type": ServiceType.STORAGE,
        "subtype": ServiceSubtype.STORAGE,
        "size": "1024",
        "timestamp": timestamp,
    }
    response = await api_client.post("/usage/storage", json=request_payload)

    assert response.json() == {}
    assert response.status_code == 201
    assert mock_sqs_manager.client.send_message.await_count == 1
