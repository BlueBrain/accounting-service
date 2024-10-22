"""Price api."""

from fastapi import APIRouter, status

from app.dependencies import RepoGroupDep
from app.schema.api import AddPriceIn, AddPriceOut, ApiResponse
from app.service import price

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_price(
    repos: RepoGroupDep,
    price_request: AddPriceIn,
) -> ApiResponse[AddPriceOut]:
    """Add a new price."""
    result = await price.add_price(repos, price_request)
    return ApiResponse[AddPriceOut](
        message="Price added",
        data=AddPriceOut.model_validate(result, from_attributes=True),
    )
