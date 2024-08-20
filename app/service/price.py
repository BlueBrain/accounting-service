"""Price service."""

from decimal import Decimal

from app.db.model import Price
from app.errors import ensure_result
from app.repository.group import RepositoryGroup
from app.schema.api import AddPriceIn


def calculate_cost(price: Price, usage_value: int, *, include_fixed_cost: bool = True) -> Decimal:
    """Return the cost for a job."""
    cost = price.multiplier * usage_value
    if include_fixed_cost:
        cost += price.fixed_cost
    return cost


async def add_price(repos: RepositoryGroup, price_request: AddPriceIn) -> Price:
    """Add a price."""
    if price_request.vlab_id:
        with ensure_result(error_message="Virtual lab not found"):
            await repos.account.get_vlab_account(vlab_id=price_request.vlab_id)
    return await repos.price.add_price(price_request.model_dump())
