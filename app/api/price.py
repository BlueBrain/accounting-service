"""Price api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import AddPriceRequest, AddPriceResponse
from app.service import price

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_price(
    repos: RepoGroupDep,
    price_request: AddPriceRequest,
) -> AddPriceResponse:
    """Add a new price."""
    result = await price.add_price(repos, price_request)
    return AddPriceResponse.model_validate(result, from_attributes=True)
