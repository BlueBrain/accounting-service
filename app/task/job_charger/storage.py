"""Storage charger."""

from app.config import settings
from app.db.session import database_session_manager
from app.repository.group import RepositoryGroup
from app.service.charge_storage import charge_storage
from app.task.job_charger.base import BaseTask


class PeriodicStorageCharger(BaseTask):
    """PeriodicStorageCharger."""

    def __init__(self, name: str, initial_delay: int = 0) -> None:
        """Init the task."""
        super().__init__(
            name=name,
            initial_delay=initial_delay,
            loop_sleep=settings.CHARGE_LONGRUN_LOOP_SLEEP,
            error_sleep=settings.CHARGE_LONGRUN_ERROR_SLEEP,
        )

    async def _run_once(self) -> None:  # noqa: PLR6301
        async with database_session_manager.session() as db:
            repos = RepositoryGroup(db=db)
            # get and charge finished jobs not charged or partially charged
            jobs = await repos.job.get_storage_finished_to_be_charged()
            await charge_storage(repos=repos, jobs=jobs)
            # get and charge running jobs
            jobs = await repos.job.get_storage_running()
            await charge_storage(
                repos=repos,
                jobs=jobs,
                min_charging_interval=settings.CHARGE_STORAGE_MIN_CHARGING_INTERVAL,
                min_charging_amount=settings.CHARGE_STORAGE_MIN_CHARGING_AMOUNT,
            )
