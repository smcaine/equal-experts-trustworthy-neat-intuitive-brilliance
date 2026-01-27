import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils import get_settings


@pytest.fixture(scope="module")
def test_client():
    """Provide a TestClient instance for end-to-end tests.

    The fixture yields a `TestClient` created from the application
    instance exported by `app.main`. It ensures proper startup/shutdown
    behavior around each test.
    """
    get_settings.cache_clear()
    with TestClient(app) as client:
        yield client
