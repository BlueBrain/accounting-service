"""Main entry point."""

import asyncio
import contextlib

import uvicorn
import uvloop

from app.config import settings
from app.db.session import database_session_manager
from app.logger import configure_logging
from app.task.job_charger.longrun import PeriodicLongrunCharger
from app.task.job_charger.oneshot import PeriodicOneshotCharger
from app.task.job_charger.storage import PeriodicStorageCharger
from app.task.queue_consumer.longrun import LongrunQueueConsumer
from app.task.queue_consumer.oneshot import OneshotQueueConsumer
from app.task.queue_consumer.storage import StorageQueueConsumer


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
            log_config=None,
        )
    )
    longrun_consumer = LongrunQueueConsumer(
        name="longrun-consumer",
        queue_name=settings.SQS_LONGRUN_QUEUE_NAME,
        initial_delay=1,
    )
    oneshot_consumer = OneshotQueueConsumer(
        name="oneshot-consumer",
        queue_name=settings.SQS_ONESHOT_QUEUE_NAME,
        initial_delay=2,
    )
    storage_consumer = StorageQueueConsumer(
        name="storage-consumer",
        queue_name=settings.SQS_STORAGE_QUEUE_NAME,
        initial_delay=3,
    )
    longrun_charger = PeriodicLongrunCharger(name="longrun-charger", initial_delay=4)
    oneshot_charger = PeriodicOneshotCharger(name="oneshot-charger", initial_delay=5)
    storage_charger = PeriodicStorageCharger(name="storage-charger", initial_delay=6)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(longrun_consumer.run_forever(), name=longrun_consumer.name)
            tg.create_task(oneshot_consumer.run_forever(), name=oneshot_consumer.name)
            tg.create_task(storage_consumer.run_forever(), name=storage_consumer.name)
            tg.create_task(longrun_charger.run_forever(), name=longrun_charger.name)
            tg.create_task(oneshot_charger.run_forever(), name=oneshot_charger.name)
            tg.create_task(storage_charger.run_forever(), name=storage_charger.name)
            tg.create_task(server.serve(), name="uvicorn")
    finally:
        await database_session_manager.close()


with contextlib.suppress(KeyboardInterrupt):
    uvloop.run(main())
