"""Budget api."""

from fastapi import APIRouter

from app.dependencies import RepoGroupDep
from app.schema.api import ApiResponse, AssignBudgetIn, MoveBudgetIn, ReverseBudgetIn, TopUpIn
from app.service import budget as budget_service

router = APIRouter()


@router.post("/top-up")
async def top_up(repos: RepoGroupDep, top_up_request: TopUpIn) -> ApiResponse:
    """Top-up a virtual lab account."""
    await budget_service.top_up(
        repos,
        vlab_id=top_up_request.vlab_id,
        amount=top_up_request.amount,
    )
    return ApiResponse(
        message="Top-up operation executed",
    )


@router.post("/assign")
async def assign(repos: RepoGroupDep, assign_request: AssignBudgetIn) -> ApiResponse:
    """Move a budget from vlab_id to proj_id."""
    await budget_service.assign(
        repos,
        vlab_id=assign_request.vlab_id,
        proj_id=assign_request.proj_id,
        amount=assign_request.amount,
    )
    return ApiResponse(
        message="Assign budget operation executed",
    )


@router.post("/reverse")
async def reverse(repos: RepoGroupDep, reverse_request: ReverseBudgetIn) -> ApiResponse:
    """Move a budget from proj_id to vlab_id."""
    await budget_service.reverse(
        repos,
        vlab_id=reverse_request.vlab_id,
        proj_id=reverse_request.proj_id,
        amount=reverse_request.amount,
    )
    return ApiResponse(
        message="Reverse budget operation executed",
    )


@router.post("/move")
async def move(repos: RepoGroupDep, move_request: MoveBudgetIn) -> ApiResponse:
    """Move a budget between projects belonging to the same virtual lab."""
    await budget_service.move(
        repos,
        vlab_id=move_request.vlab_id,
        debited_from=move_request.debited_from,
        credited_to=move_request.credited_to,
        amount=move_request.amount,
    )
    return ApiResponse(
        message="Move budget operation executed",
    )
