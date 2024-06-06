import pytest
from app import main as test_module
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    with TestClient(test_module.app) as client:
        yield client
