import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

import pytest
import sqlalchemy as sa
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession, get_session
from asyncpg.pgproto.pgproto import timedelta
from botocore.stub import Stubber
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import application
from app.config import settings
from app.constants import D0, ServiceSubtype, ServiceType, TransactionType
from app.db.model import Account, Job, Journal, Ledger, Price
from app.db.session import database_session_manager
from app.utils import utcnow

from tests.constants import PROJ_ID, PROJ_ID_2, RSV_ID, RSV_ID_2, SYS_ID, UUIDS, VLAB_ID
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
        sa.insert(Account),
        [
            {
                "id": SYS_ID,
                "account_type": "SYS",
                "parent_id": None,
                "name": "OBP",
                "balance": -3000,
            },
            {
                "id": VLAB_ID,
                "account_type": "VLAB",
                "parent_id": None,
                "name": "Test vlab_01",
                "balance": 2000,
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
    await db.commit()


@pytest.fixture
async def _db_price(db):
    """Populate the price table."""
    valid_from = datetime.fromisoformat("2024-01-01T00:00:00Z")
    await db.execute(
        sa.insert(Price),
        [
            {
                "id": 1,
                "service_type": ServiceType.ONESHOT,
                "service_subtype": ServiceSubtype.ML_LLM,
                "valid_from": valid_from,
                "valid_to": None,
                "fixed_cost": D0,
                "multiplier": Decimal("0.00001"),
                "vlab_id": None,
            },
            {
                "id": 2,
                "service_type": ServiceType.LONGRUN,
                "service_subtype": ServiceSubtype.SINGLE_CELL_SIM,
                "valid_from": valid_from,
                "valid_to": None,
                "fixed_cost": Decimal("1.5"),
                "multiplier": Decimal("0.01"),
                "vlab_id": None,
            },
            {
                "id": 3,
                "service_type": ServiceType.STORAGE,
                "service_subtype": ServiceSubtype.STORAGE,
                "valid_from": valid_from,
                "valid_to": None,
                "fixed_cost": D0,
                "multiplier": Decimal("0.001"),
                "vlab_id": None,
            },
        ],
    )
    await db.commit()


@pytest.fixture
async def _db_job(db, _db_account):
    """Populate the job table."""
    dt = utcnow() - timedelta(minutes=10)
    await db.execute(
        sa.insert(Job),
        [
            {
                "id": UUIDS.JOB[0],
                "vlab_id": UUIDS.VLAB[0],
                "proj_id": UUIDS.PROJ[0],
                "service_type": ServiceType.ONESHOT,
                "service_subtype": ServiceSubtype.ML_LLM,
                "reserved_at": dt,
                "started_at": dt + timedelta(seconds=10),
                "last_alive_at": None,
                "last_charged_at": dt + timedelta(seconds=10),
                "finished_at": dt + timedelta(seconds=10),
                "cancelled_at": None,
                "reservation_params": {"count": 1000},
                "usage_params": {"count": 1500},
            },
            {
                "id": UUIDS.JOB[1],
                "vlab_id": UUIDS.VLAB[0],
                "proj_id": UUIDS.PROJ[0],
                "service_type": ServiceType.LONGRUN,
                "service_subtype": ServiceSubtype.SINGLE_CELL_SIM,
                "reserved_at": dt,
                "started_at": dt + timedelta(seconds=30),
                "last_alive_at": dt + timedelta(seconds=60),
                "last_charged_at": dt + timedelta(seconds=120),
                "finished_at": dt + timedelta(seconds=120),
                "cancelled_at": None,
                "reservation_params": {"instances": 1, "duration": 60},
                "usage_params": {"instances": 1},
            },
            {
                "id": UUIDS.JOB[2],
                "vlab_id": UUIDS.VLAB[0],
                "proj_id": UUIDS.PROJ[0],
                "service_type": ServiceType.STORAGE,
                "service_subtype": ServiceSubtype.STORAGE,
                "reserved_at": None,
                "started_at": dt + timedelta(seconds=120),
                "last_alive_at": dt + timedelta(seconds=120),
                "last_charged_at": dt + timedelta(seconds=240),
                "finished_at": dt + timedelta(seconds=240),
                "cancelled_at": None,
                "usage_params": {"size": 1000},
            },
        ],
    )
    await db.commit()


@pytest.fixture
async def _db_ledger(db, _db_account, _db_price, _db_job):
    """Populate the journal and ledger table."""
    dt = utcnow() - timedelta(minutes=1)
    await db.execute(
        sa.insert(Journal),
        [
            {
                "id": 1,
                "transaction_datetime": dt,
                "transaction_type": TransactionType.RESERVE,
                "job_id": UUIDS.JOB[0],
                "price_id": 1,  # oneshot.ml-llm
            },
            {
                "id": 2,
                "transaction_datetime": dt,
                "transaction_type": TransactionType.CHARGE_ONESHOT,
                "job_id": UUIDS.JOB[0],
                "price_id": 1,  # oneshot.ml-llm
            },
            {
                "id": 3,
                "transaction_datetime": dt,
                "transaction_type": TransactionType.CHARGE_ONESHOT,
                "job_id": UUIDS.JOB[0],
                "price_id": 1,  # oneshot.ml-llm
            },
        ],
    )
    await db.execute(
        sa.insert(Ledger),
        [
            {
                "account_id": UUIDS.PROJ[0],
                "journal_id": 1,
                "amount": -1000 * Decimal("0.00001"),
            },
            {
                "account_id": UUIDS.RSV[0],
                "journal_id": 1,
                "amount": 1000 * Decimal("0.00001"),
            },
            {
                "account_id": UUIDS.RSV[0],
                "journal_id": 2,
                "amount": -1000 * Decimal("0.00001"),
            },
            {
                "account_id": UUIDS.SYS,
                "journal_id": 2,
                "amount": 1000 * Decimal("0.00001"),
            },
            {
                "account_id": UUIDS.PROJ[0],
                "journal_id": 3,
                "amount": -500 * Decimal("0.00001"),
            },
            {
                "account_id": UUIDS.SYS,
                "journal_id": 3,
                "amount": 500 * Decimal("0.00001"),
            },
        ],
    )
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
