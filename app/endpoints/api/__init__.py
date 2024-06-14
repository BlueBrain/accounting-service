"""Api endpoints."""

from fastapi import APIRouter

from app.endpoints.api import v1

router = APIRouter()
router.include_router(v1.router, prefix="/v1")
