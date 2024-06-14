"""Root endpoints."""

from fastapi import APIRouter

from app.endpoints import api, root

router = APIRouter()
router.include_router(root.router)
router.include_router(api.router, prefix="/api")
