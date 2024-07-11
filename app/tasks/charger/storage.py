"""Storage charger."""

import asyncio

from app.config import settings
from app.db.session import database_session_manager
from app.logger import get_logger
from app.repositories.group import RepositoryGroup
from app.services.charge_storage import charge_storage_jobs

L = get_logger(__name__)


class PeriodicStorageCharger:
    """PeriodicStorageCharger."""

    def __init__(self, initial_delay: int = 0) -> None:
        """Init the PeriodicStorageCharger.

        Args:
            initial_delay: initial delay in seconds, before starting the task.
        """
        self._initial_delay = initial_delay
        self._success = 0
        self._failure = 0

    def reset_stats(self) -> None:
        """Reset the task statistics."""
        self._success = 0
        self._failure = 0

    def get_stats(self) -> dict[str, int]:
        """Return the task statistics."""
        return {
            "counter": self.counter,
            "success": self._success,
            "failure": self._failure,
        }

    @property
    def counter(self) -> int:
        """Return the total number of loops executed."""
        return self._success + self._failure

    async def run_forever(self, limit: int = 0) -> None:
        """Periodically check and charge for storage.

        Args:
            limit: maximum number of loops, or 0 to run forever.
        """
        L.info("Starting %s", self.__class__.__name__)
        await asyncio.sleep(self._initial_delay)
        while True:
            try:
                async with database_session_manager.session() as db:
                    repos = RepositoryGroup(db=db)
                    await charge_storage_jobs(
                        repos=repos,
                        min_charging_interval=settings.CHARGE_STORAGE_MIN_CHARGING_INTERVAL,
                        min_charging_amount=settings.CHARGE_STORAGE_MIN_CHARGING_AMOUNT,
                    )
            except Exception:  # noqa: BLE001
                L.exception("Internal error in %s", self.__class__.__name__)
                sleep = settings.CHARGE_STORAGE_ERROR_SLEEP
                self._failure += 1
            else:
                sleep = settings.CHARGE_STORAGE_LOOP_SLEEP
                self._success += 1
            if 0 < limit <= self.counter:
                break
            await asyncio.sleep(sleep)
