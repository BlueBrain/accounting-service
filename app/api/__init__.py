"""Web api."""

from fastapi import APIRouter

from app.api import account, budget, reservation, root

router = APIRouter()
router.include_router(root.router)
router.include_router(account.router, prefix="/api/account", tags=["account"])
router.include_router(budget.router, prefix="/api/budget", tags=["budget"])
router.include_router(reservation.router, prefix="/api/reservation", tags=["reservation"])
