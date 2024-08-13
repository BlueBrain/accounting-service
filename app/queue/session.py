"""SQS session utils."""

from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any

from aiobotocore.client import AioBaseClient

from app.logger import L
from app.queue.utils import CreateSQSClientProtocol, create_default_sqs_client, get_queue_url


class SQSManager:
    """SQSManager."""

    def __init__(self) -> None:
        """Init the SQSManager."""
        self._exit_stack = AsyncExitStack()
        self._client: AioBaseClient | None = None
        self._client_config: dict[str, Any] | None = None
        self._queue_names: list[str] = []
        self._queue_urls: dict[str, str] = {}
        self._create_sqs_client: CreateSQSClientProtocol = create_default_sqs_client

    def configure(
        self,
        *,
        queue_names: list[str],
        client_config: dict[str, Any] | None = None,
        create_sqs_client: CreateSQSClientProtocol | None = None,
    ) -> None:
        """Configure the SQS Manager.

        Args:
            queue_names: list of names, used to fetch the urls when entering the context manager.
            client_config: config dictionary passed to ``botocore.config.Config()``.
            create_sqs_client: optional async context manager used to create a sqs client.
        """
        if self._client:
            err = "SQS manager cannot be configured inside its own context manager"
            raise RuntimeError(err)
        self._queue_names = queue_names
        self._client_config = client_config
        self._create_sqs_client = create_sqs_client or create_default_sqs_client

    async def __aenter__(self) -> None:
        """Initialize the SQS client."""
        self._client = await self._exit_stack.enter_async_context(
            self._create_sqs_client(client_config=self._client_config)
        )
        L.info("SQS client has been initialized")
        self._queue_urls = {
            name: await get_queue_url(sqs_client=self._client, queue_name=name)
            for name in self._queue_names
        }
        L.info("SQS queue urls have been retrieved", **self._queue_urls)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the SQS client."""
        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)
        self._client = None
        L.info("SQS client has been closed")

    @property
    def client(self) -> AioBaseClient:
        """Return the SQS client."""
        if not self._client:
            err = "SQS client can be accessed only inside the context manager"
            raise RuntimeError(err)
        return self._client

    @property
    def queue_urls(self) -> dict[str, str]:
        """Return the dict of queue urls."""
        return self._queue_urls


sqs_manager = SQSManager()
