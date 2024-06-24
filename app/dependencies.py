"""Dependencies for endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import database_session_manager


async def database_session_factory() -> AsyncIterator[AsyncSession]:
    """Yield a database session, to be used as a dependency."""
    async with database_session_manager.session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(database_session_factory)]
