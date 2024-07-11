"""Dependencies for endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import database_session_manager
from app.repositories.account import AccountRepository
from app.repositories.group import RepositoryGroup
from app.repositories.job import JobRepository
from app.repositories.ledger import LedgerRepository


async def _database_session_factory() -> AsyncIterator[AsyncSession]:
    """Yield a database session, to be used as a dependency."""
    async with database_session_manager.session() as session:
        yield session


def _account_repo(db: "SessionDep") -> AccountRepository:
    return AccountRepository(db=db)


def _job_repo(db: "SessionDep") -> JobRepository:
    return JobRepository(db=db)


def _ledger_repo(db: "SessionDep") -> LedgerRepository:
    return LedgerRepository(db=db)


def _repo_group(db: "SessionDep") -> RepositoryGroup:
    return RepositoryGroup(db=db)


SessionDep = Annotated[AsyncSession, Depends(_database_session_factory)]
AccountRepoDep = Annotated[AccountRepository, Depends(_account_repo)]
JobRepoDep = Annotated[JobRepository, Depends(_job_repo)]
LedgerRepoDep = Annotated[LedgerRepository, Depends(_ledger_repo)]
RepoGroupDep = Annotated[RepositoryGroup, Depends(_repo_group)]
