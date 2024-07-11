import json
from datetime import UTC, datetime
from uuid import UUID

import pytest
import sqlalchemy as sa

from app.config import settings
from app.db.models import Event, Job
from app.queue.consumer import storage as test_module

from tests.constants import PROJ_ID, VLAB_ID


def _get_queue_url_response(queue_url):
    return {"QueueUrl": queue_url}


def _get_receive_message_response(message_id, receipt_handle, message_body):
    message = {
        "Attributes": {
            "MessageGroupId": "MyMessageGroupId",
            "SenderId": "127.0.0.1",
            "SentTimestamp": "1719477803995",
            "SequenceNumber": "1",
        },
        "Body": json.dumps(message_body),
        "MD5OfBody": "987174cdadf8efffd6a255a1b23e8488",
        "MessageId": message_id,
        "ReceiptHandle": receipt_handle,
    }
    return {"Messages": [message]}


def _prepare_stub(stub, queue_url, message_id, receipt_handle, message_body):
    stub.add_response(
        "get_queue_url",
        service_response=_get_queue_url_response(queue_url),
        expected_params={
            "QueueName": "storage.fifo",
        },
    )
    stub.add_response(
        "receive_message",
        service_response=_get_receive_message_response(message_id, receipt_handle, message_body),
        expected_params={
            "QueueUrl": queue_url,
            "MessageSystemAttributeNames": [
                "MessageGroupId",
                "SenderId",
                "SentTimestamp",
                "SequenceNumber",
            ],
            "MaxNumberOfMessages": 1,
            "VisibilityTimeout": 30,
            "WaitTimeSeconds": 20,
        },
    )
    stub.add_response(
        "delete_message",
        service_response={},
        expected_params={
            "QueueUrl": queue_url,
            "ReceiptHandle": receipt_handle,
        },
    )


@pytest.mark.usefixtures("_db_account")
async def test_consume(sqs_stubber, sqs_client_factory, db):
    queue_name = settings.SQS_STORAGE_QUEUE_NAME
    queue_url = "http://queue:9324/000000000000/storage.fifo"
    message_id = "3e7a742a-3450-4ca2-a2ee-b044a525d16f"
    receipt_handle = "3e7a742a-3450-4ca2-a2ee-b044a525d16f#b0880329-82c2-4f39-92e3-d0d3d70e7dbf"
    message_body = {
        "type": "storage",
        "proj_id": PROJ_ID,
        "size": "1073741824",
        "timestamp": "1719477803993",
    }
    _prepare_stub(sqs_stubber, queue_url, message_id, receipt_handle, message_body)

    consumer = test_module.StorageQueueConsumer(
        queue_name=queue_name,
        create_sqs_client=sqs_client_factory,
    )
    assert consumer.queue_name == queue_name

    await consumer.run_forever(limit=1)

    sqs_stubber.assert_no_pending_responses()

    # verify the content of the db
    query = sa.select(Event)
    records = (await db.scalars(query)).all()
    assert len(records) == 1
    assert records[0].message_id == UUID(message_id)

    query = sa.select(Job)
    records = (await db.scalars(query)).all()
    assert len(records) == 1
    assert records[0].service_type == "storage"
    assert records[0].vlab_id == UUID(VLAB_ID)
    assert records[0].proj_id == UUID(PROJ_ID)
    assert records[0].units == 1073741824
    assert records[0].started_at == datetime.fromtimestamp(1719477803.993, tz=UTC)
