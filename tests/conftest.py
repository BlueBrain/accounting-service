import pytest
from fastapi.testclient import TestClient

from app.application import app


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client
