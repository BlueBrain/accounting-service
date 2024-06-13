def test_root(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 302
    assert response.next_request.url.path == "/docs"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_version(client):
    response = client.get("/version")

    assert response.status_code == 200
    response_json = response.json()
    assert set(response_json) == {"app_name", "app_version", "commit_sha"}
    assert response_json["app_name"] == "accounting-service"
    assert response_json["app_version"] is not None
    assert response_json["commit_sha"] is not None


def test_error(client):
    response = client.get("/error")

    assert response.status_code == 400
    assert response.json() == {"message": "ApiError: Generic error returned for testing purposes"}
