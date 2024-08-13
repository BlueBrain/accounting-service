"""Queue utils."""

from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Protocol

import aiobotocore.session
import botocore.config
from aiobotocore.client import AioBaseClient


class CreateSQSClientProtocol(Protocol):
    """Protocol defining the async function create_default_sqs_client."""

    def __call__(  # noqa: D102
        self, client_config: dict[str, Any] | None = None
    ) -> AbstractAsyncContextManager[AioBaseClient]: ...


@asynccontextmanager
async def create_default_sqs_client(
    client_config: dict[str, Any] | None = None,
) -> AsyncIterator[AioBaseClient]:
    """Return a new aiobotocore client.

    The client can handle multiple requests, and it should be created only when needed,
    because the creation might be relatively expensive.

    Boto should get credentials from ~/.aws/credentials or the environment.
    In particular, the following keys are required:

    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_DEFAULT_REGION
    - AWS_ENDPOINT_URL

    Args:
        client_config: config dictionary to be passed to ``botocore.config.Config()``.
    """
    config = botocore.config.Config(**client_config) if client_config else None
    session = aiobotocore.session.get_session()
    async with session.create_client("sqs", config=config) as client:
        yield client


async def get_queue_url(sqs_client: AioBaseClient, queue_name: str) -> str:
    """Return the queue url for a named queue."""
    response = await sqs_client.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]
