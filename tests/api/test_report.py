from unittest.mock import ANY

import pytest

from tests.constants import UUIDS


@pytest.mark.usefixtures("_db_ledger")
@pytest.mark.parametrize(
    ("url", "extra_expected_data"),
    [
        (
            "/report/system",
            {
                "vlab_id": str(UUIDS.VLAB[0]),
                "proj_id": str(UUIDS.PROJ[0]),
            },
        ),
        (
            f"/report/virtual-lab/{UUIDS.VLAB[0]}",
            {
                "proj_id": str(UUIDS.PROJ[0]),
            },
        ),
        (
            f"/report/project/{UUIDS.PROJ[0]}",
            {},
        ),
    ],
)
async def test_get_report(api_client, url, extra_expected_data):
    response = await api_client.get(url, params={"page_size": 2, "page": 1})

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "items": [
            {
                **extra_expected_data,
                "job_id": str(UUIDS.JOB[0]),
                "type": "oneshot",
                "subtype": "ml-llm",
                "amount": "0.01500",
                "reserved_amount": "0.01000",
                "count": 1500,
                "reserved_count": 1000,
                "reserved_at": ANY,
                "started_at": ANY,
            },
            {
                **extra_expected_data,
                "job_id": str(UUIDS.JOB[1]),
                "type": "longrun",
                "subtype": "single-cell-sim",
                "amount": "0",  # no ledger records
                "reserved_amount": "0",  # no ledger records
                "duration": 90,
                "reserved_duration": 60,
                "reserved_at": ANY,
                "started_at": ANY,
                "finished_at": ANY,
                "cancelled_at": None,
            },
        ],
        "meta": {
            "page": 1,
            "page_size": 2,
            "total_items": 3,
            "total_pages": 2,
        },
        "links": {
            "self": f"{api_client.base_url}{url}?page_size=2&page=1",
            "first": f"{api_client.base_url}{url}?page_size=2&page=1",
            "last": f"{api_client.base_url}{url}?page_size=2&page=2",
            "next": f"{api_client.base_url}{url}?page_size=2&page=2",
            "prev": None,
        },
    }

    response = await api_client.get(url, params={"page_size": 2, "page": 2})

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "items": [
            {
                **extra_expected_data,
                "job_id": str(UUIDS.JOB[2]),
                "type": "storage",
                "subtype": "storage",
                "amount": "0",  # no ledger records
                "started_at": ANY,
                "finished_at": ANY,
                "duration": 120,
                "size": 1000,
            },
        ],
        "meta": {
            "page": 2,
            "page_size": 2,
            "total_items": 3,
            "total_pages": 2,
        },
        "links": {
            "self": f"{api_client.base_url}{url}?page_size=2&page=2",
            "first": f"{api_client.base_url}{url}?page_size=2&page=1",
            "last": f"{api_client.base_url}{url}?page_size=2&page=2",
            "next": None,
            "prev": f"{api_client.base_url}{url}?page_size=2&page=1",
        },
    }

    response = await api_client.get(url, params={"page_size": 2, "page": 3})

    assert response.status_code == 200, f"unexpected response {response.text!r}"
    assert response.json()["data"] == {
        "items": [],
        "meta": {
            "page": 3,
            "page_size": 2,
            "total_items": 3,
            "total_pages": 2,
        },
        "links": {
            "self": f"{api_client.base_url}{url}?page_size=2&page=3",
            "first": f"{api_client.base_url}{url}?page_size=2&page=1",
            "last": f"{api_client.base_url}{url}?page_size=2&page=2",
            "next": None,
            "prev": f"{api_client.base_url}{url}?page_size=2&page=2",
        },
    }


@pytest.mark.parametrize(
    ("url", "expected_message"),
    [
        (f"/report/virtual-lab/{UUIDS.SYS}", "Virtual lab not found"),
        (f"/report/project/{UUIDS.SYS}", "Project not found"),
    ],
)
async def test_get_report_not_found(api_client, url, expected_message):
    response = await api_client.get(url, params={"page_size": 2, "page": 1})

    assert response.status_code == 404, f"unexpected response {response.text!r}"
    assert response.json() == {
        "details": None,
        "error_code": "ENTITY_NOT_FOUND",
        "message": expected_message,
    }
