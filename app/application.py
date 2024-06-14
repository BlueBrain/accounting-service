"""API entry points."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.status import HTTP_302_FOUND

from app.api.v1.base import base_router as v1_router
from app.config import settings
from app.errors import ApiError
from app.logger import L


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Execute actions on server startup and shutdown."""
    L.info("PID: %s", os.getpid())
    L.info("CPU count: %s", os.cpu_count())
    yield
    L.info("Stopping the application")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:  # noqa: ARG001
    """Handle API errors to be returned to the client."""
    msg = f"{exc.__class__.__name__}: {exc}"
    L.warning(msg)
    return JSONResponse(status_code=exc.status_code, content={"message": msg})


@app.get("/")
async def root() -> Response:
    """Root endpoint."""
    return RedirectResponse(url="/docs", status_code=HTTP_302_FOUND)


@app.get("/health")
async def health() -> dict:
    """Health endpoint."""
    return {
        "status": "OK",
    }


@app.get("/version")
async def version() -> dict:
    """Version endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "commit_sha": settings.COMMIT_SHA,
    }


@app.get("/error", include_in_schema=False)
async def error() -> None:
    """Error endpoint to test generic error responses."""
    msg = "Generic error returned for testing purposes"
    raise ApiError(msg)


app.include_router(v1_router, prefix=settings.API_V1)
