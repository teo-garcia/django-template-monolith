import pytest
from django.test import Client


@pytest.mark.django_db
def test_service_info_available() -> None:
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_openapi_docs_available() -> None:
    client = Client()
    response = client.get("/docs", follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_openapi_schema_lists_operational_and_api_routes() -> None:
    client = Client()
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/" in paths
    assert "/health/live" in paths
    assert "/health/ready" in paths
    assert "/health" in paths
    assert "/metrics" in paths
    assert "/api/v1/tasks/" in paths
    assert "/api/v1/tasks/{task_id}" in paths
    schemas = response.json()["components"]["schemas"]
    assert "ErrorEnvelope" in schemas
    assert "TaskListResponse" in schemas
    assert (
        paths["/api/v1/tasks/"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/TaskListResponse"
    )
