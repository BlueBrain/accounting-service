import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.config import settings
from app.db import session as test_module


async def test_database_session_manager_lifecycle():
    database_session_manager = test_module.DatabaseSessionManager()
    assert database_session_manager._engine is None

    with pytest.raises(RuntimeError, match="DB engine not initialized"):
        async with database_session_manager.session():
            pass

    database_session_manager.initialize(
        url=settings.DB_URI,
        pool_size=settings.DB_POOL_SIZE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    assert isinstance(database_session_manager._engine, AsyncEngine)

    async with database_session_manager.session() as session:
        assert isinstance(session, AsyncSession)

    with pytest.raises(RuntimeError, match="DB engine already initialized"):
        database_session_manager.initialize(url=settings.DB_URI)

    await database_session_manager.close()
    assert database_session_manager._engine is None

    with pytest.raises(RuntimeError, match="DB engine not initialized"):
        await database_session_manager.close()
