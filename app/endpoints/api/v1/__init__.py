"""V1 endpoints."""

from fastapi import APIRouter

from app.endpoints.api.v1 import reservation, virtual_lab

router = APIRouter()
router.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
router.include_router(virtual_lab.router, prefix="/virtual-lab", tags=["virtual-lab"])
