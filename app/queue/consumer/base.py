"""Base consumer module."""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from typing import Any

import botocore.exceptions
from aiobotocore.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import QueueMessageStatus
from app.db.session import database_session_manager
from app.logger import get_logger
from app.repositories.queue_message import QueueMessageRepository

L = get_logger(__name__)


class QueueLoggerAdapter(logging.LoggerAdapter):
    """QueueLoggerAdapter to add the queue name to the logs."""

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        """Process a log message."""
        return f"[{self.extra['queue']}] {msg}", kwargs


class QueueConsumer(ABC):
    """Generic queue consumer."""

    def __init__(self, endpoint_url: str, queue_name: str, initial_delay: int = 0) -> None:
        """Init the QueueConsumer.

        Args:
            endpoint_url: url of the queue.
            queue_name: name of the queue.
            initial_delay: initial delay in seconds, before starting to consume the queue.
        """
        self._endpoint_url = endpoint_url
        self._queue_name = queue_name
        self._initial_delay = initial_delay
        self.logger = QueueLoggerAdapter(L, extra={"queue": queue_name})

    @abstractmethod
    async def consume(self, msg: dict[str, Any], db: AsyncSession) -> None:
        """Consume the message."""

    async def consume_wrapper(self, msg: dict[str, Any]) -> bool:
        """Wrap the message handler and return True if successful, False otherwise."""
        async with database_session_manager.session() as db:
            repo = QueueMessageRepository(db=db)
            try:
                await self.consume(msg=msg, db=db)
            except Exception:
                self.logger.exception("Error processing message")
                await repo.upsert(
                    msg=msg,
                    queue_name=self._queue_name,
                    status=QueueMessageStatus.FAILED,
                    error=traceback.format_exc(),
                )
                return False
            else:
                await repo.upsert(
                    msg=msg,
                    queue_name=self._queue_name,
                    status=QueueMessageStatus.COMPLETED,
                )
                return True

    async def run_forever(self) -> None:
        """Retrieve and dispatch messages from the queue until the task is cancelled.

        # Boto should get credentials from ~/.aws/credentials or the environment:

            - AWS_ACCESS_KEY_ID
            - AWS_SECRET_ACCESS_KEY
            - AWS_DEFAULT_REGION
        """
        session = get_session()
        async with session.create_client("sqs", endpoint_url=self._endpoint_url) as sqs:
            self.logger.info("Pulling messages off the queue %s", self._queue_name)
            response = await sqs.get_queue_url(QueueName=self._queue_name)
            queue_url = response["QueueUrl"]
            await asyncio.sleep(self._initial_delay)
            while True:
                try:
                    response = await sqs.receive_message(
                        QueueUrl=queue_url,
                        MessageSystemAttributeNames=[
                            "MessageGroupId",
                            "SenderId",
                            "SentTimestamp",
                            "SequenceNumber",
                        ],
                        MaxNumberOfMessages=5,
                        VisibilityTimeout=30,
                        WaitTimeSeconds=20,  # enable long polling
                    )
                    messages = response.get("Messages", [])
                    self.logger.info("Received %s messages", len(messages))
                    for msg in messages:
                        receipt_handle = msg["ReceiptHandle"]
                        if await self.consume_wrapper(msg=msg):
                            await sqs.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=receipt_handle,
                            )
                except botocore.exceptions.ClientError:
                    self.logger.exception("Client error")
                    await asyncio.sleep(settings.SQS_CLIENT_ERROR_SLEEP)
