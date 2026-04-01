import pytest
from ninja.testing import TestClient

from app.main import api


@pytest.fixture
def client() -> TestClient:
    return TestClient(api)
