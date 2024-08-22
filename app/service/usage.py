"""Usage service."""

from app.config import settings
from app.logger import L
from app.queue.session import SQSManager
from app.schema.queue import LongrunEvent, OneshotEvent, StorageEvent


def calculate_longrun_usage_value(
    instances: int,
    instance_type: str | None,
    duration: float,
) -> int:
    """Return the usage_value.

    Args:
        instances: number of instances.
        instance_type: type of instance.
        duration: duration in seconds.
    """
    if instance_type:
        # TODO: consider instance_type?
        L.warning("instance_type is ignored")
    return int(instances * duration)


def calculate_oneshot_usage_value(count: int) -> int:
    """Return the usage_value.

    Args:
        count: number representing the usage.
    """
    return int(count)


def calculate_storage_usage_value(size: int, duration: float) -> int:
    """Return the usage_value.

    Args:
        size: number of bytes.
        duration: duration in seconds.
    """
    return int(size * duration)


async def add_oneshot_usage(event: OneshotEvent, sqs_manager: SQSManager) -> None:
    """Add a oneshot event to the queue."""
    msg_body = event.model_dump_json()
    await sqs_manager.client.send_message(
        QueueUrl=sqs_manager.queue_urls[settings.SQS_ONESHOT_QUEUE_NAME],
        MessageBody=msg_body,
        MessageGroupId=str(event.proj_id),
    )


async def add_longrun_usage(event: LongrunEvent, sqs_manager: SQSManager) -> None:
    """Add a longrun event to the queue."""
    msg_body = event.model_dump_json()
    await sqs_manager.client.send_message(
        QueueUrl=sqs_manager.queue_urls[settings.SQS_LONGRUN_QUEUE_NAME],
        MessageBody=msg_body,
        MessageGroupId=str(event.proj_id),
    )


async def add_storage_usage(event: StorageEvent, sqs_manager: SQSManager) -> None:
    """Add a storage event to the queue."""
    msg_body = event.model_dump_json()
    await sqs_manager.client.send_message(
        QueueUrl=sqs_manager.queue_urls[settings.SQS_STORAGE_QUEUE_NAME],
        MessageBody=msg_body,
        MessageGroupId=str(event.proj_id),
    )
