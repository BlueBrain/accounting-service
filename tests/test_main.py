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
    assert response.json() == {
        "app_name": "accounting-service",
        "app_version": None,
        "commit_sha": None,
    }


def test_error(client):
    response = client.get("/error")

    assert response.status_code == 400
    assert response.json() == {"message": "ApiError: Generic error returned for testing purposes"}
