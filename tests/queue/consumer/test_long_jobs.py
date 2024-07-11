from app.config import settings
from app.queue.consumer import long_jobs as test_module


async def test_consume(sqs_client_factory):
    queue_name = settings.SQS_LONG_JOBS_QUEUE_NAME
    consumer = test_module.LongJobsQueueConsumer(
        queue_name=queue_name,
        create_sqs_client=sqs_client_factory,
    )
    assert consumer.queue_name == queue_name

    # await consumer.run_forever(limit=1)
