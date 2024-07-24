"""Long job charger."""

from app.config import settings
from app.db.session import database_session_manager
from app.repository.group import RepositoryGroup
from app.service.charge_long_job import charge_long_job
from app.task.job_charger.base import BaseTask


class PeriodicLongJobCharger(BaseTask):
    """PeriodicLongJobCharger."""

    def __init__(self, name: str, initial_delay: int = 0) -> None:
        """Init the task."""
        super().__init__(
            name=name,
            initial_delay=initial_delay,
            loop_sleep=settings.CHARGE_LONG_JOB_LOOP_SLEEP,
            error_sleep=settings.CHARGE_LONG_JOB_ERROR_SLEEP,
        )

    async def _run_once(self) -> None:  # noqa: PLR6301
        async with database_session_manager.session() as db:
            repos = RepositoryGroup(db=db)
            await charge_long_job(
                repos=repos,
                min_charging_interval=settings.CHARGE_LONG_JOB_MIN_CHARGING_INTERVAL,
                min_charging_amount=settings.CHARGE_LONG_JOB_MIN_CHARGING_AMOUNT,
            )
