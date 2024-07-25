"""Budget service."""

from decimal import Decimal
from http import HTTPStatus
from uuid import UUID

from sqlalchemy.exc import NoResultFound

from app.constants import AccountType, TransactionType
from app.errors import ApiError, ApiErrorCode
from app.repository.group import RepositoryGroup
from app.utils import utcnow


async def top_up(repos: RepositoryGroup, vlab_id: UUID, amount: Decimal) -> None:
    """Top-up a virtual lab account."""
    now = utcnow()
    try:
        system_account = await repos.account.get_system_account()
    except NoResultFound as err:
        raise ApiError(
            message="System account not found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
    try:
        vlab = await repos.account.get_vlab_account(vlab_id=vlab_id)
    except NoResultFound as err:
        raise ApiError(
            message="Virtual lab not found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=system_account.id,
        credited_to=vlab.id,
        transaction_datetime=now,
        transaction_type=TransactionType.TOP_UP,
    )


async def assign(repos: RepositoryGroup, vlab_id: UUID, proj_id: UUID, amount: Decimal) -> None:
    """Move a budget from vlab_id to proj_id."""
    now = utcnow()
    try:
        accounts = await repos.account.get_accounts_by_proj_id(
            proj_id=proj_id, for_update={AccountType.VLAB}
        )
    except NoResultFound as err:
        raise ApiError(
            message="Account not found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
    if accounts.vlab.id != vlab_id:
        raise ApiError(
            message="The project doesn't belong to the virtual-lab",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    if accounts.vlab.balance < amount:
        raise ApiError(
            message="Insufficient funds in the virtual-lab account",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=accounts.vlab.id,
        credited_to=accounts.proj.id,
        transaction_datetime=now,
        transaction_type=TransactionType.ASSIGN_BUDGET,
    )


async def reverse(repos: RepositoryGroup, vlab_id: UUID, proj_id: UUID, amount: Decimal) -> None:
    """Move a budget from proj_id to vlab_id."""
    now = utcnow()
    try:
        accounts = await repos.account.get_accounts_by_proj_id(
            proj_id=proj_id, for_update={AccountType.PROJ}
        )
    except NoResultFound as err:
        raise ApiError(
            message="Account not found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
    if accounts.vlab.id != vlab_id:
        raise ApiError(
            message="The project doesn't belong to the virtual-lab",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    if accounts.proj.balance < amount:
        raise ApiError(
            message="Insufficient funds in the project account",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=accounts.proj.id,
        credited_to=accounts.vlab.id,
        transaction_datetime=now,
        transaction_type=TransactionType.REVERSE_BUDGET,
    )


async def move(
    repos: RepositoryGroup, vlab_id: UUID, debited_from: UUID, credited_to: UUID, amount: Decimal
) -> None:
    """Move a budget between projects belonging to the same virtual lab."""
    now = utcnow()
    try:
        debited_accounts = await repos.account.get_accounts_by_proj_id(
            proj_id=debited_from, for_update={AccountType.PROJ}
        )
        credited_accounts = await repos.account.get_accounts_by_proj_id(proj_id=credited_to)
    except NoResultFound as err:
        raise ApiError(
            message="Account not found",
            error_code=ApiErrorCode.ENTITY_NOT_FOUND,
            http_status_code=HTTPStatus.NOT_FOUND,
        ) from err
    if debited_from == credited_to:
        raise ApiError(
            message="The debited and credited accounts must be different",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    if debited_accounts.vlab.id != vlab_id:
        raise ApiError(
            message="The debited project doesn't belong to the virtual-lab",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    if credited_accounts.vlab.id != vlab_id:
        raise ApiError(
            message="The credited project doesn't belong to the virtual-lab",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    if debited_accounts.proj.balance < amount:
        raise ApiError(
            message="Insufficient funds in the debited account",
            error_code=ApiErrorCode.INVALID_REQUEST,
        )
    await repos.ledger.insert_transaction(
        amount=amount,
        debited_from=debited_from,
        credited_to=credited_to,
        transaction_datetime=now,
        transaction_type=TransactionType.MOVE_BUDGET,
    )
