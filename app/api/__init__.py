"""Web api."""

from fastapi import APIRouter

from app.api import account, reservation, root

router = APIRouter()
router.include_router(root.router)
router.include_router(account.router, prefix="/api/account", tags=["account"])
router.include_router(reservation.router, prefix="/api/reservation", tags=["reservation"])
