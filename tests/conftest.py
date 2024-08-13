import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

import pytest
import sqlalchemy as sa
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession, get_session
from botocore.stub import Stubber
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import application
from app.config import settings
from app.constants import D0, ServiceSubtype, ServiceType
from app.db.model import Account, Price
from app.db.session import database_session_manager
from app.utils import utcnow

from tests.constants import PROJ_ID, PROJ_ID_2, RSV_ID, RSV_ID_2, SYS_ID, VLAB_ID
from tests.utils import truncate_tables


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def _database_context():
    database_session_manager.initialize(
        url=settings.DB_URI,
        pool_size=settings.DB_POOL_SIZE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )


@pytest.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with database_session_manager.session() as session:
        yield session


@pytest.fixture(autouse=True)
async def _db_cleanup(db):
    yield
    await db.rollback()
    await truncate_tables(db)


@pytest.fixture
async def app():
    return application.app


@pytest.fixture
async def api_client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
def sqs_session() -> AioSession:
    """Always return the same sqs session for performance reasons."""
    return get_session()


@pytest.fixture(scope="session")
async def sqs_client(sqs_session) -> AsyncIterator[AioBaseClient]:
    """Always return the same sqs client for performance reasons."""
    async with sqs_session.create_client(
        "sqs",
        endpoint_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
def sqs_client_factory(sqs_client):
    """Always return the same sqs client for performance reasons."""

    @asynccontextmanager
    async def factory(client_config=None):  # noqa: ARG001
        yield sqs_client

    return factory


@pytest.fixture
async def sqs_stubber(sqs_client) -> AsyncIterator[Stubber]:
    """Return a new stubber for each test."""
    with Stubber(sqs_client) as stubber:
        yield stubber


@pytest.fixture
async def _db_account(db):
    """Populate the account table."""
    await db.execute(
        sa.insert(Account).values(
            [
                {
                    "id": SYS_ID,
                    "account_type": "SYS",
                    "parent_id": None,
                    "name": "OBP",
                    "balance": -2000,
                },
                {
                    "id": VLAB_ID,
                    "account_type": "VLAB",
                    "parent_id": None,
                    "name": "Test vlab_01",
                    "balance": 1000,
                },
                {
                    "id": PROJ_ID,
                    "account_type": "PROJ",
                    "parent_id": VLAB_ID,
                    "name": "Test vlab_01/proj_01",
                    "balance": 400,
                },
                {
                    "id": RSV_ID,
                    "account_type": "RSV",
                    "parent_id": PROJ_ID,
                    "name": "Test vlab_01/proj_01/RESERVATION",
                    "balance": 100,
                },
                {
                    "id": PROJ_ID_2,
                    "account_type": "PROJ",
                    "parent_id": VLAB_ID,
                    "name": "Test vlab_01/proj_02",
                    "balance": 500,
                },
                {
                    "id": RSV_ID_2,
                    "account_type": "RSV",
                    "parent_id": PROJ_ID_2,
                    "name": "Test vlab_01/proj_02/RESERVATION",
                    "balance": 0,
                },
            ],
        )
    )
    # commit b/c the test might be using a new transaction, for example when calling an endpoint
    await db.commit()


@pytest.fixture
async def _db_price(db):
    """Populate the price table."""
    await db.execute(
        sa.insert(Price).values(
            [
                {
                    "service_type": ServiceType.STORAGE,
                    "service_subtype": ServiceSubtype.STORAGE,
                    "valid_from": utcnow(),
                    "valid_to": None,
                    "fixed_cost": D0,
                    "multiplier": Decimal("0.001"),
                    "vlab_id": None,
                },
                {
                    "service_type": ServiceType.ONESHOT,
                    "service_subtype": ServiceSubtype.ML_LLM,
                    "valid_from": utcnow(),
                    "valid_to": None,
                    "fixed_cost": D0,
                    "multiplier": Decimal("0.00001"),
                    "vlab_id": None,
                },
                {
                    "service_type": ServiceType.LONGRUN,
                    "service_subtype": ServiceSubtype.SINGLE_CELL_SIM,
                    "valid_from": utcnow(),
                    "valid_to": None,
                    "fixed_cost": Decimal("1.5"),
                    "multiplier": Decimal("0.01"),
                    "vlab_id": None,
                },
            ],
        )
    )
    # commit b/c the test might be using a new transaction, for example when calling an endpoint
    await db.commit()


@pytest.fixture
def mock_uuid():
    i = 0

    def _fake_uuid():
        nonlocal i
        i += 1
        return UUID(f"{i:032x}")

    with patch("uuid.uuid4", side_effect=_fake_uuid, autospec=True) as m:
        yield m
