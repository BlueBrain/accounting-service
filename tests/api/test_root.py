from app.config import settings


async def test_root(api_client):
    response = await api_client.get("/", follow_redirects=False)

    assert response.status_code == 302
    assert response.next_request.url.path == f"{settings.ROOT_PATH}/docs"


async def test_health(api_client):
    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


async def test_version(api_client):
    response = await api_client.get("/version")

    assert response.status_code == 200
    response_json = response.json()
    assert set(response_json) == {"app_name", "app_version", "commit_sha"}
    assert response_json["app_name"] == "accounting-service"
    assert response_json["app_version"] is not None
    assert response_json["commit_sha"] is not None


async def test_error(api_client):
    response = await api_client.get("/error")

    assert response.status_code == 400
    assert response.json() == {"message": "ApiError: Generic error returned for testing purposes"}
