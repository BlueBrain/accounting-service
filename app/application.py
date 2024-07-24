"""API entry points."""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api import router
from app.config import settings
from app.errors import ApiError
from app.logger import L


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Execute actions on server startup and shutdown."""
    L.info(
        "Starting application [PID={}, CPU_COUNT={}, ENVIRONMENT={}]",
        os.getpid(),
        os.cpu_count(),
        settings.ENVIRONMENT,
    )
    try:
        yield {}
    except asyncio.CancelledError as err:
        # this can happen if the task is cancelled without sending SIGINT
        L.info("Ignored {} in lifespan", err)
    finally:
        L.info("Stopping application")


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
    root_path=settings.ROOT_PATH,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
