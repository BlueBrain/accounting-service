"""Virtual lab endpoints."""

from uuid import UUID

from fastapi import APIRouter

router = APIRouter()


@router.get("/{virtual_lab_id}")
async def get_virtual_lab(virtual_lab_id: UUID) -> dict:
    """Return the virtual lab."""
    return {
        "virtual_lab_id": virtual_lab_id,
    }
