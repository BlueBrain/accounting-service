"""DB utils."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def try_nested(
    db: AsyncSession,
    on_error: Callable[[], None] | None = None,
    on_success: Callable[[], None] | None = None,
) -> AsyncIterator[None]:
    """Begin a nested transaction and call the provided synchronous callbacks if provided."""
    try:
        async with db.begin_nested():
            yield
    except Exception:  # noqa: BLE001
        if on_error:
            on_error()
    else:
        if on_success:
            on_success()
