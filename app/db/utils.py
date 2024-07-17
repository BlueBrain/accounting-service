"""DB utils."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def try_nested(db: AsyncSession, err_callback: Callable[[], None]) -> AsyncIterator[None]:
    """Begin a nested transaction and call the provided sync callback in case of error."""
    try:
        async with db.begin_nested():
            yield
    except Exception:  # noqa: BLE001
        err_callback()
