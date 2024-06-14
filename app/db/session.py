"""Database session utils."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.logger import L


class DatabaseSessionFactory:
    """DatabaseSessionFactory."""

    def __init__(self) -> None:
        """Init the factory."""
        self._engine: AsyncEngine | None = None

    async def initialize(self, url: str, **kwargs) -> None:
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

    async def __call__(self) -> AsyncIterator[AsyncSession]:
        """Return a new database session."""
        if not self._engine:
            err = "DB engine not initialized"
            raise RuntimeError(err)
        session = AsyncSession(
            self._engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


database_session_factory = DatabaseSessionFactory()
