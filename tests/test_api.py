from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invalid_file_type():
    files = {
        "file": (
            "test.txt",
            b"Hello World",
            "text/plain"
        )
    }

    response = client.post(
        "/api/files/",
        files=files
    )

    assert response.status_code == 400


def test_file_not_found():
    response = client.get(
        "/api/files/non-existing-id"
    )

    assert response.status_code == 404