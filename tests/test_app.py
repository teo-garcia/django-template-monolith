import pytest
from django.test import Client


@pytest.mark.django_db
def test_service_info_available() -> None:
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


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
    assert "/api/v1/tasks" in paths
    assert "/api/v1/tasks/{task_id}" in paths
    schemas = response.json()["components"]["schemas"]
    assert "ErrorEnvelope" in schemas
    assert "SuccessEnvelope" in schemas
    assert "TaskListResponse" in schemas

    # Successful payloads travel inside the envelope, so the documented schema
    # must describe the wrapper with the payload under `data`.
    list_schema = paths["/api/v1/tasks"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert list_schema["allOf"][0]["$ref"] == "#/components/schemas/SuccessEnvelope"
    assert list_schema["allOf"][1]["properties"]["data"]["$ref"] == "#/components/schemas/TaskListResponse"

    # Health is parsed by orchestrators and must stay unwrapped.
    health_response = paths["/health"]["get"]["responses"]["200"]
    health_content = health_response.get("content", {}).get("application/json")
    if health_content and "schema" in health_content:
        assert "allOf" not in health_content["schema"]


def test_unknown_route_uses_error_envelope() -> None:
    client = Client()
    response = client.get(
        "/missing",
        headers={"x-request-id": "00000000-0000-4000-8000-000000000001"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "statusCode": 404,
        "timestamp": response.json()["timestamp"],
        "path": "/missing",
        "method": "GET",
        "message": "Not Found",
        "error": "NotFound",
        "meta": {"requestId": "00000000-0000-4000-8000-000000000001"},
    }
