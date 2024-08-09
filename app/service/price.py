"""Price service."""

from decimal import Decimal

from app.db.model import Price


def calculate_cost(price: Price, usage_value: int, *, include_fixed_cost: bool = True) -> Decimal:
    """Return the cost for a job."""
    cost = price.multiplier * usage_value
    if include_fixed_cost:
        cost += price.fixed_cost
    return cost
