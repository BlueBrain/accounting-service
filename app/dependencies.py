"""Dependencies for endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import database_session_manager
from app.repositories.group import RepositoryGroup


async def _database_session_factory() -> AsyncIterator[AsyncSession]:
    """Yield a database session, to be used as a dependency."""
    async with database_session_manager.session() as session:
        yield session


def _repo_group(db: "SessionDep") -> RepositoryGroup:
    return RepositoryGroup(db=db)


SessionDep = Annotated[AsyncSession, Depends(_database_session_factory)]
RepoGroupDep = Annotated[RepositoryGroup, Depends(_repo_group)]
