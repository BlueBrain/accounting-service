import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession, get_session
from botocore.stub import Stubber
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import app
from app.config import settings
from app.db.session import database_session_manager

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


@pytest.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    async with database_session_manager.session() as session:
        yield session


@pytest.fixture()
async def db_cleanup(db):
    yield db
    await truncate_tables(db)


@pytest.fixture()
async def api_client() -> AsyncIterator[AsyncClient]:
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
    async def factory():
        yield sqs_client

    return factory


@pytest.fixture()
async def sqs_stubber(sqs_client) -> AsyncIterator[Stubber]:
    """Return a new stubber for each test."""
    with Stubber(sqs_client) as stubber:
        yield stubber
