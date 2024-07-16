"""Web api."""

from fastapi import APIRouter

from app.api import base, reservation, virtual_lab

router = APIRouter()
router.include_router(base.router)
router.include_router(reservation.router, prefix="/api/reservation", tags=["reservation"])
router.include_router(virtual_lab.router, prefix="/api/virtual-lab", tags=["virtual-lab"])
