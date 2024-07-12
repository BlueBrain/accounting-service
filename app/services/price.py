"""Cost service."""

from decimal import Decimal
from uuid import UUID

from app.constants import ServiceType


async def calculate_running_cost(
    vlab_id: UUID,  # noqa: ARG001
    service_type: ServiceType,  # noqa: ARG001
    service_subtype: str | None,  # noqa: ARG001
    units: int,
) -> Decimal:
    """Return the cost for a job."""
    # TODO: to be implemented
    return Decimal(units) * 10


async def calculate_fixed_cost(
    vlab_id: UUID,  # noqa: ARG001
    service_type: ServiceType,  # noqa: ARG001
    service_subtype: str | None,  # noqa: ARG001
) -> Decimal:
    """Return the cost for a job."""
    # TODO: to be implemented
    return Decimal(1)
