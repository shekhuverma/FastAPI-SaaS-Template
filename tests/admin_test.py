from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_login(login_credentials):
    response = client.post("/login", data=login_credentials)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
