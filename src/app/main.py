"""API entry points."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.config import configs
from app.errors import ApiError
from app.logger import L

from app.api.v1.base import base_router as v1_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Execute actions on server startup and shutdown."""
    L.info("PID: %s", os.getpid())
    L.info("CPU count: %s", os.cpu_count())
    yield
    L.info("Stopping the application")


app = FastAPI(
    title=configs.APP_NAME,
    debug=configs.APP_DEBUG,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def client_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """Handle application errors to be returned to the client."""
    # pylint: disable=unused-argument
    msg = f"{exc.__class__.__name__}: {exc}"
    L.warning(msg)
    return JSONResponse(status_code=exc.status_code, content={"message": msg})


@app.get("/")
async def root():
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
        "app_name": configs.APP_NAME,
        "app_version": configs.APP_VERSION,
        "commit_sha": configs.COMMIT_SHA,
    }


app.include_router(v1_router, prefix=configs.API_V1)
