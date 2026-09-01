import pytest
from django.test import Client


@pytest.mark.django_db
def test_liveness_reports_no_dependency_checks() -> None:
    response = Client().get("/health/live")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str)
    # Probing dependencies here would let an outage restart a healthy process.
    assert "checks" not in data


@pytest.mark.django_db
def test_readiness_uses_the_shared_health_contract() -> None:
    response = Client().get("/health/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str)
    assert data["checks"]["database"] == "up"
    assert data["checks"]["redis"] == "up"


@pytest.mark.django_db
def test_health_agrees_with_readiness() -> None:
    client = Client()
    overall = client.get("/health").json()
    ready = client.get("/health/ready").json()

    assert overall["status"] in ("ok", "degraded", "down")
    # Reporting different statuses for the same failure was drift, not a feature.
    assert overall["status"] == ready["status"]
    assert overall["checks"] == ready["checks"]
