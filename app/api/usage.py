"""Usage api.

Messages are pushed to the queue with minimal validation for better performance.
They are fully validated and processed when retrieved from the queue.
"""

from fastapi import APIRouter, status

from app.dependencies import SQSManagerDep
from app.schema.queue import LongrunEvent, OneshotEvent, StorageEvent
from app.service import usage

router = APIRouter()


@router.post("/oneshot", status_code=status.HTTP_201_CREATED)
async def add_oneshot_usage(event: OneshotEvent, sqs_manager: SQSManagerDep) -> dict:
    """Add a new usage for oneshot job."""
    await usage.add_oneshot_usage(event, sqs_manager=sqs_manager)
    return {}


@router.post("/longrun", status_code=status.HTTP_201_CREATED)
async def add_longrun_usage(event: LongrunEvent, sqs_manager: SQSManagerDep) -> dict:
    """Add a new usage for longrun job."""
    await usage.add_longrun_usage(event, sqs_manager=sqs_manager)
    return {}


@router.post("/storage", status_code=status.HTTP_201_CREATED)
async def add_storage_usage(event: StorageEvent, sqs_manager: SQSManagerDep) -> dict:
    """Add a new usage for storage."""
    await usage.add_storage_usage(event, sqs_manager=sqs_manager)
    return {}
