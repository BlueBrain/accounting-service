"""Queue utils."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiobotocore.session
from aiobotocore.client import AioBaseClient


@asynccontextmanager
async def create_default_sqs_client() -> AsyncIterator[AioBaseClient]:
    """Return a new aiobotocore client.

    The client can handle multiple requests, and it should be created only when needed,
    because the creation might be relatively expensive.

    Boto should get credentials from ~/.aws/credentials or the environment.
    In particular, the following keys are required:

    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_DEFAULT_REGION
    - AWS_ENDPOINT_URL
    """
    session = aiobotocore.session.get_session()
    async with session.create_client("sqs") as client:
        yield client


async def get_queue_url(sqs_client: AioBaseClient, queue_name: str) -> str:
    """Return the queue url for a named queue."""
    response = await sqs_client.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]
