"""Web api."""

from fastapi import APIRouter

from app.api import reservation, root, virtual_lab

router = APIRouter()
router.include_router(root.router)
router.include_router(reservation.router, prefix="/api/reservation", tags=["reservation"])
router.include_router(virtual_lab.router, prefix="/api/virtual-lab", tags=["virtual-lab"])
