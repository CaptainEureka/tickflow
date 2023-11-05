from typing import Generator
import pytest

from tickflow.app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
