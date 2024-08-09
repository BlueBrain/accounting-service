"""Price repository module."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import null, or_

from app.constants import ServiceSubtype, ServiceType
from app.db.model import Price
from app.errors import ApiError, ApiErrorCode
from app.repository.base import BaseRepository


class PriceRepository(BaseRepository):
    """PriceRepository."""

    async def _get_vlab_price(
        self,
        vlab_id: UUID | None,
        service_type: ServiceType,
        service_subtype: ServiceSubtype,
        usage_datetime: datetime,
    ) -> Price | None:
        """Return the price for the specified vlab."""
        query = (
            sa.select(Price)
            .where(
                Price.service_type == service_type,
                Price.service_subtype == service_subtype,
                Price.vlab_id == vlab_id,
                Price.valid_from <= usage_datetime,
                or_(
                    Price.valid_to == null(),
                    Price.valid_to > usage_datetime,
                ),
            )
            .order_by(Price.valid_from.desc())
            # .limit(1)
        )
        return (await self.db.execute(query)).scalar_one_or_none()

    async def get_price(
        self,
        vlab_id: UUID,
        service_type: ServiceType,
        service_subtype: ServiceSubtype,
        usage_datetime: datetime,
    ) -> Price:
        """Return the price for the specified vlab, or fallback to the default price."""
        price = await self._get_vlab_price(
            vlab_id=vlab_id,
            service_type=service_type,
            service_subtype=service_subtype,
            usage_datetime=usage_datetime,
        )
        if not price:
            price = await self._get_vlab_price(
                vlab_id=None,
                service_type=service_type,
                service_subtype=service_subtype,
                usage_datetime=usage_datetime,
            )
        if not price:
            msg = f"Missing price for: {vlab_id} {service_type} {service_subtype} {usage_datetime}"
            raise ApiError(message=msg, error_code=ApiErrorCode.ENTITY_NOT_FOUND)
        return price
