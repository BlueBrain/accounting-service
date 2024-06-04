import pytest
from fastapi.testclient import TestClient

from app import main as test_module


@pytest.fixture
def client():
    with TestClient(test_module.app) as client:
        yield client
