"""Account repository module."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_, true

from app.constants import AccountType
from app.db.models import Account
from app.logger import get_logger
from app.repositories.base import BaseRepository

L = get_logger(__name__)


class AccountRepository(BaseRepository):
    """AccountRepository."""

    async def get_system_account(self) -> Account:
        """Return the system account."""
        query = sa.select(Account).where(Account.account_type == AccountType.SYS)
        return (await self.db.execute(query)).scalar_one()

    async def get_generic_account(self, account_id: UUID, account_type: AccountType) -> Account:
        """Return the account for the given account id and type."""
        query = sa.select(Account).where(
            and_(
                Account.account_type == account_type,
                Account.id == account_id,
                Account.enabled == true(),
            )
        )
        return (await self.db.execute(query)).scalar_one()

    async def get_vlab_account(self, vlab_id: UUID) -> Account:
        """Return the virtual lab account for the given virtual lab id."""
        return await self.get_generic_account(account_id=vlab_id, account_type=AccountType.VLAB)

    async def get_proj_account(self, proj_id: UUID) -> Account:
        """Return the project account for the given project and virtual lab ids."""
        return await self.get_generic_account(account_id=proj_id, account_type=AccountType.PROJ)

    async def get_reservation_account(self, proj_id: UUID) -> Account:
        """Return the reservation account for the given project and virtual lab ids."""
        query = sa.select(Account).where(
            and_(
                Account.account_type == AccountType.RSV,
                Account.parent_id == proj_id,
                Account.enabled == true(),
            )
        )
        return (await self.db.execute(query)).scalar_one()
