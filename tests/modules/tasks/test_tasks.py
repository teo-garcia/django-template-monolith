import json

import pytest
from django.core.cache import cache
from django.test import Client, override_settings

API_PREFIX = "/api/v1"
TASKS_BASE_URL = f"{API_PREFIX}/tasks"


def assert_error_envelope(data: dict[str, object], status_code: int, method: str) -> None:
    assert data["success"] is False
    assert data["statusCode"] == status_code
    assert data["method"] == method
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["path"], str)
    assert isinstance(data["message"], str)
    assert isinstance(data["error"], str)
    meta = data["meta"]
    assert isinstance(meta, dict)
    assert isinstance(meta["requestId"], str)


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.django_db(transaction=True)
class TestTasksCRUD:
    def test_create_task(self, client: Client) -> None:
        response = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Test task", "description": "A test task", "priority": 3}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test task"
        assert data["description"] == "A test task"
        assert data["status"] == "PENDING"
        assert data["priority"] == 3
        assert "id" in data

    def test_list_tasks(self, client: Client) -> None:
        client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Task for listing"}),
            content_type="application/json",
        )
        response = client.get(f"{TASKS_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        assert data["meta"]["total"] >= 1
        assert data["meta"]["page"] == 1
        assert data["meta"]["pageSize"] == 20

    def test_list_tasks_paginates_results(self, client: Client) -> None:
        client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "First", "priority": 1}),
            content_type="application/json",
        )
        client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Second", "priority": 2}),
            content_type="application/json",
        )

        response = client.get(f"{TASKS_BASE_URL}/?page=1&pageSize=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["meta"] == {"total": 2, "page": 1, "pageSize": 1}

    def test_list_tasks_supports_status_and_priority_filters(self, client: Client) -> None:
        client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Low pending", "priority": 1, "status": "PENDING"}),
            content_type="application/json",
        )
        client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "High in progress", "priority": 5, "status": "IN_PROGRESS"}),
            content_type="application/json",
        )

        response = client.get(f"{TASKS_BASE_URL}/?status=IN_PROGRESS&priority=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["status"] == "IN_PROGRESS"
        assert data["data"][0]["priority"] >= 5

    def test_get_task(self, client: Client) -> None:
        create_resp = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Task to get"}),
            content_type="application/json",
        )
        task_id = create_resp.json()["id"]
        response = client.get(f"{TASKS_BASE_URL}/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Task to get"

    def test_update_task(self, client: Client) -> None:
        create_resp = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Task to update"}),
            content_type="application/json",
        )
        task_id = create_resp.json()["id"]
        response = client.patch(
            f"{TASKS_BASE_URL}/{task_id}",
            data=json.dumps({"title": "Updated title", "status": "IN_PROGRESS"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["status"] == "IN_PROGRESS"

    def test_delete_task(self, client: Client) -> None:
        create_resp = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Task to delete"}),
            content_type="application/json",
        )
        task_id = create_resp.json()["id"]
        response = client.delete(f"{TASKS_BASE_URL}/{task_id}")
        assert response.status_code == 204

        get_resp = client.get(f"{TASKS_BASE_URL}/{task_id}")
        assert get_resp.status_code == 404


@pytest.mark.django_db(transaction=True)
class TestTasksNotFound:
    def test_get_nonexistent_task(self, client: Client) -> None:
        response = client.get(f"{TASKS_BASE_URL}/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert_error_envelope(response.json(), 404, "GET")

    def test_delete_nonexistent_task(self, client: Client) -> None:
        response = client.delete(f"{TASKS_BASE_URL}/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
class TestTasksValidation:
    def test_create_task_empty_title_rejected(self, client: Client) -> None:
        response = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": ""}),
            content_type="application/json",
        )
        assert response.status_code == 422
        assert_error_envelope(response.json(), 422, "POST")

    def test_create_task_invalid_priority_rejected(self, client: Client) -> None:
        response = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Bad priority", "priority": 99}),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_task_invalid_status_rejected(self, client: Client) -> None:
        response = client.post(
            f"{TASKS_BASE_URL}/",
            data=json.dumps({"title": "Bad status", "status": "INVALID"}),
            content_type="application/json",
        )
        assert response.status_code == 422


@pytest.mark.django_db(transaction=True)
@override_settings(RATELIMIT_RATE="1/m")
def test_tasks_api_is_rate_limited(client: Client) -> None:
    cache.clear()

    first_response = client.get(f"{TASKS_BASE_URL}/")
    second_response = client.get(f"{TASKS_BASE_URL}/")

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert_error_envelope(second_response.json(), 429, "GET")
