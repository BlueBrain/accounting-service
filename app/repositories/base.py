"""Base repository module."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """BaseRepository."""

    def __init__(self, db: AsyncSession) -> None:
        """Init the repository."""
        self.db = db
