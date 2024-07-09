"""Domain entities."""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseAccount(BaseModel):
    """BaseAccount."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    balance: Decimal
    enabled: bool


class SysAccount(BaseAccount):
    """SysAccount."""


class VlabAccount(BaseAccount):
    """VlabAccount."""


class ProjAccount(BaseAccount):
    """ProjAccount."""

    vlab_id: Annotated[UUID, Field(alias="parent_id")]


class RsvAccount(BaseAccount):
    """RsvAccount."""

    proj_id: Annotated[UUID, Field(alias="parent_id")]


class Accounts(BaseModel):
    """Accounts."""

    vlab: VlabAccount
    proj: ProjAccount
    rsv: RsvAccount
