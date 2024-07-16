"""Abstract task."""

import asyncio
from abc import ABC, abstractmethod

from app.logger import get_logger

L = get_logger(__name__)


class BaseTask(ABC):
    """BaseTask."""

    def __init__(
        self, name: str, initial_delay: float = 0, loop_sleep: float = 1, error_sleep: float = 10
    ) -> None:
        """Init the task.

        Args:
            name: name of the task.
            initial_delay: initial delay in seconds, before starting the task.
            loop_sleep: number of seconds to wait after a loop without errors.
            error_sleep: number of seconds to wait after a loop with errors.
        """
        self._name = name
        self._initial_delay = initial_delay
        self._loop_sleep = loop_sleep
        self._error_sleep = error_sleep
        self._success = 0
        self._failure = 0

    @property
    def name(self) -> str:
        """Return the name of the task."""
        return self._name

    def reset_stats(self) -> None:
        """Reset the task statistics."""
        self._success = 0
        self._failure = 0

    def get_stats(self) -> dict[str, int]:
        """Return the task statistics."""
        return {
            "counter": self._counter,
            "success": self._success,
            "failure": self._failure,
        }

    @property
    def _counter(self) -> int:
        """Return the total number of loops executed."""
        return self._success + self._failure

    @abstractmethod
    async def _run_once(self) -> None:
        """Execute one loop."""

    async def run_forever(self, limit: int = 0) -> None:
        """Run the main loop.

        Args:
            limit: maximum number of loops, or 0 to run forever.
        """
        L.info("[%s] Starting...", self.__class__.__name__)
        await asyncio.sleep(self._initial_delay)
        while True:
            try:
                await self._run_once()
            except Exception:  # noqa: BLE001
                self._failure += 1
                sleep = self._error_sleep
                L.exception("[%s] Error in run_once %s", self.__class__.__name__, self._failure)
            else:
                self._success += 1
                sleep = self._loop_sleep
            if 0 < limit <= self._counter:
                break
            await asyncio.sleep(sleep)
