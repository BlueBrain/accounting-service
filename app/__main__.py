"""Main entry point."""

import asyncio
import contextlib

import uvicorn
import uvloop

from app.config import settings
from app.db.session import database_session_manager
from app.logger import configure_logging
from app.queue.consumer.long_jobs import LongJobsQueueConsumer
from app.queue.consumer.short_jobs import ShortJobsQueueConsumer
from app.queue.consumer.storage import StorageQueueConsumer


async def main() -> None:
    """Init and run all the async tasks."""
    configure_logging()
    database_session_manager.initialize(
        url=settings.DB_URI,
        pool_size=settings.DB_POOL_SIZE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    server = uvicorn.Server(
        uvicorn.Config(
            "app.application:app",
            host="0.0.0.0",
            port=settings.UVICORN_PORT,
            proxy_headers=True,
            log_config=settings.LOGGING_CONFIG,
        )
    )
    storage_queue_consumer = StorageQueueConsumer(
        queue_name=settings.SQS_STORAGE_QUEUE_NAME,
        initial_delay=1,
    )
    short_jobs_queue_consumer = ShortJobsQueueConsumer(
        queue_name=settings.SQS_SHORT_JOBS_QUEUE_NAME,
        initial_delay=2,
    )
    long_jobs_queue_consumer = LongJobsQueueConsumer(
        queue_name=settings.SQS_LONG_JOBS_QUEUE_NAME,
        initial_delay=3,
    )
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(storage_queue_consumer.run_forever(), name="storage")
            tg.create_task(short_jobs_queue_consumer.run_forever(), name="short-jobs")
            tg.create_task(long_jobs_queue_consumer.run_forever(), name="long-jobs")
            tg.create_task(server.serve(), name="uvicorn")
    finally:
        await database_session_manager.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        uvloop.run(main())
