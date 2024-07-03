import pytest

from app.config import settings
from app.queue.consumer import short_jobs as test_module

pytestmark = pytest.mark.usefixtures("_db_cleanup")


async def test_consume(sqs_client_factory):
    queue_name = settings.SQS_SHORT_JOBS_QUEUE_NAME
    consumer = test_module.ShortJobsQueueConsumer(
        queue_name=queue_name,
        create_sqs_client=sqs_client_factory,
    )
    assert consumer.queue_name == queue_name

    # await consumer.run_forever(limit=1)
