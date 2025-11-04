import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    """Create a test client for our app"""
    from src.app import app
    return TestClient(app)