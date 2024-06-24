from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """BaseRepository."""

    def __init__(self, db: AsyncSession) -> None:
        """Init the repository."""
        self.db = db


def autocommit(func):
    """Automatically commit the transaction."""

    @wraps(func)
    async def wrapper(self: BaseRepository, *args, **kwargs):
        """Wrap the decorated function."""
        try:
            return await func(self, *args, **kwargs)
        except Exception:
            raise
        else:
            await self.db.commit()

    return wrapper
