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

    async def get_generic_account(
        self,
        account_id: UUID,
        account_type: AccountType,
        *,
        for_update: bool = False,
    ) -> Account:
        """Return the account for the given account id and type.

        Args:
            account_id: account UUID.
            account_type: account type.
            for_update: if True, locks the selected row against concurrent updates.
        """
        query = sa.select(Account).where(
            and_(
                Account.account_type == account_type,
                Account.id == account_id,
                Account.enabled == true(),
            )
        )
        if for_update:
            query = query.with_for_update()
        return (await self.db.execute(query)).scalar_one()

    async def get_vlab_account(self, vlab_id: UUID, *, for_update: bool = False) -> Account:
        """Return the virtual lab account for the given virtual lab id.

        Args:
            vlab_id: virtual lab UUID.
            for_update: if True, locks the selected row against concurrent updates.
        """
        return await self.get_generic_account(
            account_id=vlab_id, account_type=AccountType.VLAB, for_update=for_update
        )

    async def get_proj_account(self, proj_id: UUID, *, for_update: bool = False) -> Account:
        """Return the project account for the given project and virtual lab ids.

        Args:
            proj_id: project UUID.
            for_update: if True, lock the selected row against concurrent updates.
        """
        return await self.get_generic_account(
            account_id=proj_id, account_type=AccountType.PROJ, for_update=for_update
        )

    async def get_reservation_account(self, proj_id: UUID, *, for_update: bool = False) -> Account:
        """Return the reservation account for the given project and virtual lab ids.

        Args:
            proj_id: project UUID.
            for_update: if True, locks the selected row against concurrent updates.
        """
        query = sa.select(Account).where(
            and_(
                Account.account_type == AccountType.RSV,
                Account.parent_id == proj_id,
                Account.enabled == true(),
            )
        )
        if for_update:
            query = query.with_for_update()
        return (await self.db.execute(query)).scalar_one()
