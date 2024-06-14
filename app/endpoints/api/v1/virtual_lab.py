"""Virtual lab endpoints."""

from fastapi import APIRouter
from pydantic import UUID4

router = APIRouter()


@router.get("/{virtual_lab_id}")
async def get_virtual_lab(virtual_lab_id: UUID4) -> dict:
    """Return the virtual lab."""
    return {
        "virtual_lab_id": virtual_lab_id,
    }
