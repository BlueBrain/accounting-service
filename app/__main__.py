"""Main entry point."""

import asyncio
import contextlib

import uvicorn
import uvloop

from app.config import settings
from app.db.session import database_session_manager
from app.logger import configure_logging
from app.tasks.charger.storage import PeriodicStorageCharger
from app.tasks.consumer.long_jobs import LongJobsQueueConsumer
from app.tasks.consumer.short_jobs import ShortJobsQueueConsumer
from app.tasks.consumer.storage import StorageQueueConsumer


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
    storage_consumer = StorageQueueConsumer(
        name="storage-consumer",
        queue_name=settings.SQS_STORAGE_QUEUE_NAME,
        initial_delay=1,
    )
    short_jobs_consumer = ShortJobsQueueConsumer(
        name="short-jobs-consumer",
        queue_name=settings.SQS_SHORT_JOBS_QUEUE_NAME,
        initial_delay=2,
    )
    long_jobs_consumer = LongJobsQueueConsumer(
        name="long-jobs-consumer",
        queue_name=settings.SQS_LONG_JOBS_QUEUE_NAME,
        initial_delay=3,
    )
    storage_charger = PeriodicStorageCharger(initial_delay=4, name="storage-charger")
    short_jobs_charger = PeriodicStorageCharger(initial_delay=5, name="short-jobs-charger")
    long_jobs_charger = PeriodicStorageCharger(initial_delay=6, name="long-jobs-charger")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(storage_consumer.run_forever(), name=storage_consumer.name)
            tg.create_task(short_jobs_consumer.run_forever(), name=short_jobs_consumer.name)
            tg.create_task(long_jobs_consumer.run_forever(), name=long_jobs_consumer.name)
            tg.create_task(storage_charger.run_forever(), name=storage_charger.name)
            tg.create_task(short_jobs_charger.run_forever(), name=short_jobs_charger.name)
            tg.create_task(long_jobs_charger.run_forever(), name=long_jobs_charger.name)
            tg.create_task(server.serve(), name="uvicorn")
    finally:
        await database_session_manager.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        uvloop.run(main())
