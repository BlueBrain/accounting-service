"""Storage charger."""

from app.config import settings
from app.db.session import database_session_manager
from app.repository.group import RepositoryGroup
from app.service.charge_storage import charge_storage_jobs
from app.task.job_charger.base import BaseTask


class PeriodicStorageCharger(BaseTask):
    """PeriodicStorageCharger."""

    def __init__(self, name: str, initial_delay: int = 0) -> None:
        """Init the task."""
        super().__init__(
            name=name,
            initial_delay=initial_delay,
            loop_sleep=settings.CHARGE_LONG_JOBS_LOOP_SLEEP,
            error_sleep=settings.CHARGE_LONG_JOBS_ERROR_SLEEP,
        )

    async def _run_once(self) -> None:  # noqa: PLR6301
        async with database_session_manager.session() as db:
            repos = RepositoryGroup(db=db)
            await charge_storage_jobs(
                repos=repos,
                min_charging_interval=settings.CHARGE_STORAGE_MIN_CHARGING_INTERVAL,
                min_charging_amount=settings.CHARGE_STORAGE_MIN_CHARGING_AMOUNT,
            )
