"""API entry points."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.db.session import database_session_factory
from app.endpoints import router
from app.errors import ApiError
from app.logger import L


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Execute actions on server startup and shutdown."""
    L.info(
        "Starting application [ENVIRONMENT=%s, pid=%s, cpu_count=%s]",
        settings.ENVIRONMENT,
        os.getpid(),
        os.cpu_count(),
    )
    await database_session_factory.initialize(
        url=settings.DB_URI,
        echo=settings.DB_ECHO,
        echo_pool=settings.DB_ECHO_POOL,
        pool_size=settings.DB_POOL_SIZE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    try:
        yield {}
    finally:
        L.info("Stopping application")
        await database_session_factory.close()


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    """Handle API errors to be returned to the client."""
    msg = f"{exc.__class__.__name__}: {exc}"
    L.warning(msg)
    return JSONResponse(status_code=exc.status_code, content={"message": msg})


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
    exception_handlers={ApiError: api_error_handler},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
