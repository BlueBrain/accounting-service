"""Database session utils."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.logger import get_logger

L = get_logger(__name__)


class DatabaseSessionManager:
    """DatabaseSessionManager."""

    def __init__(self) -> None:
        """Init the manager."""
        self._engine: AsyncEngine | None = None

    def initialize(self, url: str, **kwargs) -> None:
        """Initialize the database engine."""
        if self._engine:
            err = "DB engine already initialized"
            raise RuntimeError(err)
        self._engine = create_async_engine(url, **kwargs)
        L.info("DB engine has been initialized")

    async def close(self) -> None:
        """Shut down the database engine."""
        if not self._engine:
            err = "DB engine not initialized"
            raise RuntimeError(err)
        await self._engine.dispose()
        self._engine = None
        L.info("DB engine has been closed")

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield a new database session."""
        if not self._engine:
            err = "DB engine not initialized"
            raise RuntimeError(err)
        async with AsyncSession(
            self._engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        ) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()


database_session_manager = DatabaseSessionManager()
