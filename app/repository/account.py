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
        """Return the project account for the given project id.

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
        """Return the reservation account for the given project id.

        Args:
            proj_id: project UUID.
            for_update: if True, locks the selected row against concurrent updates.
        """
        rows = await self.get_reservation_accounts(proj_ids=[proj_id], for_update=for_update)
        return rows[0]

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
        sys = await self.get_system_account()
        return Accounts(sys=sys, vlab=vlab, proj=proj, rsv=rsv)

    async def get_proj_accounts_for_vlab(self, vlab_id: UUID) -> list[ProjAccount]:
        """Return all the projects for the specified virtual-lab."""
        query = sa.select(Account).where(
            and_(
                Account.account_type == AccountType.PROJ,
                Account.parent_id == vlab_id,
                Account.enabled == true(),
            )
        )
        result = (await self.db.execute(query)).scalars()
        return [ProjAccount.model_validate(row) for row in result]

    async def get_reservation_accounts(
        self, proj_ids: list[UUID], *, for_update: bool = False
    ) -> list[RsvAccount]:
        """Return the reservation accounts for the given project ids.

        Args:
            proj_ids: list of project UUIDs.
            for_update: if True, locks the selected rows against concurrent updates.
        """
        if not proj_ids:
            return []
        query = sa.select(Account).where(
            and_(
                Account.account_type == AccountType.RSV,
                Account.parent_id.in_(proj_ids),
                Account.enabled == true(),
            )
        )
        if for_update:
            query = query.with_for_update()
        rows = (await self.db.execute(query)).scalars()
        result = [RsvAccount.model_validate(row) for row in rows]
        if len(result) < len(proj_ids):
            errmsg = "No reservation account was found for some projects"
            raise ValueError(errmsg)
        if len(result) > len(proj_ids) or len(result) > len({rec.proj_id for rec in result}):
            errmsg = "Multiple reservation accounts were found for some projects"
            raise ValueError(errmsg)
        return result

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
