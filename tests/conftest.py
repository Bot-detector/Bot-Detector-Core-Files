import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from api.app import app

@pytest.fixture
def test_client():
    """Returns a Starlette test API instance"""
    return TestClient(app)
