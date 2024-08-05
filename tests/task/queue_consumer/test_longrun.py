from app.config import settings
from app.task.queue_consumer import longrun as test_module


async def test_consume(sqs_client_factory):
    queue_name = settings.SQS_LONGRUN_QUEUE_NAME
    consumer = test_module.LongrunQueueConsumer(
        name="test-longrun-consumer",
        queue_name=queue_name,
        create_sqs_client=sqs_client_factory,
    )
    assert consumer.queue_name == queue_name

    # await consumer.run_forever(limit=1)
