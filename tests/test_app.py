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
