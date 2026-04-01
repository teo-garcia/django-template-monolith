import pytest
from django.test import Client


@pytest.mark.django_db
def test_liveness() -> None:
    client = Client()
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readiness() -> None:
    client = Client()
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


@pytest.mark.django_db
def test_health() -> None:
    client = Client()
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "database" in data["checks"]
    assert "redis" in data["checks"]
