import pytest
from aiobotocore.client import AioBaseClient

from app.config import settings
from app.queue import session as test_module


def _get_queue_url_response(queue_url):
    return {"QueueUrl": queue_url}


def _prepare_stub(stub, queue_url, queue_name):
    stub.add_response(
        "get_queue_url",
        service_response=_get_queue_url_response(queue_url),
        expected_params={
            "QueueName": queue_name,
        },
    )


async def test_sqs_manager_lifecycle(sqs_stubber, sqs_client_factory):
    sqs_manager = test_module.SQSManager()

    expected_err = "SQS client can be accessed only inside the context manager"
    with pytest.raises(RuntimeError, match=expected_err):
        _ = sqs_manager.client

    assert sqs_manager.queue_urls == {}

    queue_name = settings.SQS_STORAGE_QUEUE_NAME
    queue_url = f"http://queue:9324/000000000000/{queue_name}"
    queue_names = [queue_name]
    _prepare_stub(sqs_stubber, queue_url, queue_name)

    sqs_manager.configure(
        queue_names=queue_names,
        client_config=settings.SQS_CLIENT_CONFIG.model_dump(),
        create_sqs_client=sqs_client_factory,
    )

    async with sqs_manager:
        assert set(sqs_manager.queue_urls) == set(queue_names)
        assert isinstance(sqs_manager.client, AioBaseClient)

        expected_err = "SQS manager cannot be configured inside its own context manager"
        with pytest.raises(RuntimeError, match=expected_err):
            sqs_manager.configure(queue_names=[])

    sqs_stubber.assert_no_pending_responses()
