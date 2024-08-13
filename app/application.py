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
from app.queue.session import sqs_manager
from app.schema.api import ErrorResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Execute actions on server startup and shutdown."""
    L.info(
        "Starting application [PID={}, CPU_COUNT={}, ENVIRONMENT={}]",
        os.getpid(),
        os.cpu_count(),
        settings.ENVIRONMENT,
    )
    sqs_manager.configure(
        queue_names=[
            settings.SQS_LONGRUN_QUEUE_NAME,
            settings.SQS_ONESHOT_QUEUE_NAME,
            settings.SQS_STORAGE_QUEUE_NAME,
        ],
        client_config=settings.SQS_CLIENT_CONFIG.model_dump(),
    )
    try:
        async with sqs_manager:
            yield {}
    except asyncio.CancelledError as err:
        # this can happen if the task is cancelled without sending SIGINT
        L.info("Ignored {} in lifespan", err)
    finally:
        L.info("Stopping application")


async def api_error_handler(request: Request, exception: ApiError) -> JSONResponse:
    """Handle API errors to be returned to the client."""
    L.error("API error in {} {}: {!r}", request.method, request.url, exception)
    return JSONResponse(
        status_code=int(exception.http_status_code),
        content=ErrorResponse(
            message=exception.message,
            error_code=exception.error_code,
            details=exception.details,
        ).model_dump(),
    )


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
