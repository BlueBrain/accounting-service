"""Account repository module."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_, true

from app.constants import AccountType
from app.db.model import Account
from app.repository.base import BaseRepository
from app.schema.domain import Accounts, ProjAccount, RsvAccount, SysAccount, VlabAccount
from app.utils import create_uuid


class AccountRepository(BaseRepository):
    """AccountRepository."""

    async def get_system_account(self) -> SysAccount:
        """Return the system account."""
        query = sa.select(Account).where(Account.account_type == AccountType.SYS)
        result = (await self.db.execute(query)).scalar_one()
        return SysAccount.model_validate(result)

    async def _get_generic_account(
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

    async def get_vlab_account(self, vlab_id: UUID, *, for_update: bool = False) -> VlabAccount:
        """Return the virtual lab account for the given virtual lab id.

        Args:
            vlab_id: virtual lab UUID.
            for_update: if True, locks the selected row against concurrent updates.
        """
        result = await self._get_generic_account(
            account_id=vlab_id, account_type=AccountType.VLAB, for_update=for_update
        )
        return VlabAccount.model_validate(result)

    async def get_proj_account(self, proj_id: UUID, *, for_update: bool = False) -> ProjAccount:
        """Return the project account for the given project and virtual lab ids.

        Args:
            proj_id: project UUID.
            for_update: if True, lock the selected row against concurrent updates.
        """
        result = await self._get_generic_account(
            account_id=proj_id, account_type=AccountType.PROJ, for_update=for_update
        )
        return ProjAccount.model_validate(result)

    async def get_reservation_account(
        self, proj_id: UUID, *, for_update: bool = False
    ) -> RsvAccount:
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
        result = (await self.db.execute(query)).scalar_one()
        return RsvAccount.model_validate(result)

    async def get_accounts_by_proj_id(
        self, proj_id: UUID, *, for_update: set[AccountType] | None = None
    ) -> Accounts:
        """Return the related VLAB, PROJ, and RSV accounts for the given proj_id."""
        for_update = for_update or set()
        proj = await self.get_proj_account(
            proj_id=proj_id, for_update=AccountType.PROJ in for_update
        )
        rsv = await self.get_reservation_account(
            proj_id=proj_id, for_update=AccountType.RSV in for_update
        )
        vlab = await self.get_vlab_account(
            vlab_id=proj.vlab_id, for_update=AccountType.VLAB in for_update
        )
        return Accounts(vlab=vlab, proj=proj, rsv=rsv)

    async def _add_generic_account(self, **kwargs) -> Account:
        return (
            await self.db.execute(sa.insert(Account).values(kwargs).returning(Account))
        ).scalar_one()

    async def add_sys_account(self, account_id: UUID, name: str) -> SysAccount:
        """Add the system account. Only one system account is allowed."""
        account = await self._add_generic_account(
            account_type=AccountType.SYS,
            id=account_id,
            name=name,
        )
        return SysAccount.model_validate(account)

    async def add_vlab_account(self, account_id: UUID, name: str) -> VlabAccount:
        """Add a new virtual lab account."""
        account = await self._add_generic_account(
            account_type=AccountType.VLAB,
            id=account_id,
            name=name,
        )
        return VlabAccount.model_validate(account)

    async def add_proj_account(self, account_id: UUID, name: str, vlab_id: UUID) -> ProjAccount:
        """Add a new project account."""
        account = await self._add_generic_account(
            account_type=AccountType.PROJ,
            id=account_id,
            name=name,
            parent_id=vlab_id,
        )
        await self._add_generic_account(
            account_type=AccountType.RSV,
            id=create_uuid(),
            name=f"{name}/RESERVATION",
            parent_id=account_id,
        )
        return ProjAccount.model_validate(account)
