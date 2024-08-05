from app.config import settings
from app.task.queue_consumer import oneshot as test_module


async def test_consume(sqs_client_factory):
    queue_name = settings.SQS_ONESHOT_QUEUE_NAME
    consumer = test_module.OneshotQueueConsumer(
        name="test-oneshot-consumer",
        queue_name=queue_name,
        create_sqs_client=sqs_client_factory,
    )
    assert consumer.queue_name == queue_name

    # await consumer.run_forever(limit=1)
