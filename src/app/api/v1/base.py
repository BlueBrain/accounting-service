"""Base v1 router."""

from fastapi import APIRouter

from app.api.v1 import virtual_lab

base_router = APIRouter()

for router in [
    virtual_lab.router,
]:
    base_router.include_router(router)
