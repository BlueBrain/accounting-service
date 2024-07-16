"""Group of repositories."""

from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.account import AccountRepository
from app.repository.event import EventRepository
from app.repository.job import JobRepository
from app.repository.ledger import LedgerRepository


class RepositoryGroup:
    """Group of repositories sharing the same database session."""

    def __init__(
        self,
        db: AsyncSession,
        account_repo_class: type[AccountRepository] = AccountRepository,
        event_repo_class: type[EventRepository] = EventRepository,
        job_repo_class: type[JobRepository] = JobRepository,
        ledger_repo_class: type[LedgerRepository] = LedgerRepository,
    ) -> None:
        """Init the repository group."""
        self._db = db
        self._account_repo_class = account_repo_class
        self._event_repo_class = event_repo_class
        self._job_repo_class = job_repo_class
        self._ledger_repo_class = ledger_repo_class

    @property
    def db(self) -> AsyncSession:
        """Return the shared database session."""
        return self._db

    @cached_property
    def account(self) -> AccountRepository:
        """Return the account repository."""
        return self._account_repo_class(self.db)

    @cached_property
    def event(self) -> EventRepository:
        """Return the event repository."""
        return self._event_repo_class(self.db)

    @cached_property
    def job(self) -> JobRepository:
        """Return the job repository."""
        return self._job_repo_class(self.db)

    @cached_property
    def ledger(self) -> LedgerRepository:
        """Return the ledger repository."""
        return self._ledger_repo_class(self.db)
