# ruff: noqa: PGH004
# ruff: noqa

import logging
import time

import httpx


def _create_accounts(client, url):
    client.post(
        f"{url}/account/system",
        json={
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "",
        },
    )
    client.post(
        f"{url}/account/virtual-lab",
        json={
            "id": "36dacc3b-2423-46d3-bda3-8e90a7fdecdf",
            "name": "vlab-01",
        },
    )
    client.post(
        f"{url}/account/virtual-lab",
        json={
            "id": "4ad35399-9454-4c36-8998-4009f8414721",
            "name": "vlab-02",
        },
    )
    client.post(
        f"{url}/account/project",
        json={
            "id": "7ccfb73d-fddc-41e0-a1d6-1638005b1e7a",
            "name": "vlab-01/proj-01",
            "vlab_id": "36dacc3b-2423-46d3-bda3-8e90a7fdecdf",
        },
    )
    client.post(
        f"{url}/account/project",
        json={
            "id": "8eb248a8-672c-4158-9365-b95286cba796",
            "name": "vlab-02/proj-01",
            "vlab_id": "4ad35399-9454-4c36-8998-4009f8414721",
        },
    )
    client.post(
        f"{url}/account/project",
        json={
            "id": "970270d3-afbb-4fa0-bf18-a59977aa1af1",
            "name": "vlab-02/proj-02",
            "vlab_id": "4ad35399-9454-4c36-8998-4009f8414721",
        },
    )


def _create_budget(client, url):
    client.post(
        f"{url}/budget/top-up",
        json={
            "vlab_id": "36dacc3b-2423-46d3-bda3-8e90a7fdecdf",
            "amount": "10000",
        },
    )
    client.post(
        f"{url}/budget/top-up",
        json={
            "vlab_id": "4ad35399-9454-4c36-8998-4009f8414721",
            "amount": "100000",
        },
    )
    client.post(
        f"{url}/budget/assign",
        json={
            "vlab_id": "4ad35399-9454-4c36-8998-4009f8414721",
            "proj_id": "8eb248a8-672c-4158-9365-b95286cba796",
            "amount": "10000",
        },
    )


def _create_prices(client, url):
    client.post(
        f"{url}/price",
        json={
            "service_type": "oneshot",
            "service_subtype": "ml-llm",
            "valid_from": "2024-08-14T00:00:00Z",
            "valid_to": None,
            "fixed_cost": "0",
            "multiplier": "0.00001",
            "vlab_id": None,
        },
    )


def _create_job(client, url):
    r = client.post(
        f"{url}/reservation/oneshot",
        json={
            "type": "oneshot",
            "subtype": "ml-llm",
            "proj_id": "8eb248a8-672c-4158-9365-b95286cba796",
            "count": "10",
        },
    )
    client.post(
        f"{url}/usage/oneshot",
        json={
            "type": "oneshot",
            "subtype": "ml-llm",
            "proj_id": "8eb248a8-672c-4158-9365-b95286cba796",
            "count": "1024",
            "job_id": r.json()["data"]["job_id"],
            "timestamp": int(time.time()),
        },
    )


def log_response(response):
    logging.info("Response status: %s, Response content: %s", response.status_code, response.read())


def main(base_url):
    """Populate script to be used only to populate an empty local database via API."""
    client = httpx.Client()
    client.event_hooks["response"] = [log_response, httpx.Response.raise_for_status]
    client.get(f"{base_url}/version")
    _create_accounts(client, base_url)
    _create_budget(client, base_url)
    _create_prices(client, base_url)
    _create_job(client, base_url)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(base_url="http://localhost:8100")
