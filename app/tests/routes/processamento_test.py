import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers():
    response = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_processamento_status_code():
    headers = get_auth_headers()
    response = client.get("/v1/processamento/", headers=headers)
    assert response.status_code == 200


def test_get_processamento_returns_list():
    headers = get_auth_headers()
    response = client.get("/v1/processamento/", headers=headers)
    assert isinstance(response.json(), list)


def test_get_processamento_with_filters():
    headers = get_auth_headers()
    response = client.get("/v1/processamento/?ano=2020&category=BRANCAS&grape_type=viniferas", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert item["ano"] == 2020
        assert item["category"] == "BRANCAS"
        assert item["grape_type"] == "viniferas"