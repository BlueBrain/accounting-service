"""Dependencies for endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import database_session_factory

SessionDep = Annotated[AsyncSession, Depends(database_session_factory)]
