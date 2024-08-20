"""Dependencies for api."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.db.session import database_session_manager
from app.queue.session import SQSManager
from app.repository.group import RepositoryGroup


async def _database_session_factory() -> AsyncIterator[AsyncSession]:
    """Yield a database session, to be used as a dependency."""
    async with database_session_manager.session() as session:
        yield session


def _repo_group(db: "SessionDep") -> RepositoryGroup:
    """Return the repository group, to be used as a dependency."""
    return RepositoryGroup(db=db)


def _sqs_manager(request: Request) -> SQSManager:
    """Return the SQS manager."""
    return request.state.sqs_manager


SessionDep = Annotated[AsyncSession, Depends(_database_session_factory)]
RepoGroupDep = Annotated[RepositoryGroup, Depends(_repo_group)]
SQSManagerDep = Annotated[SQSManager, Depends(_sqs_manager)]
