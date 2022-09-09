# Fixtures defined in this file can be passed as parameters to tests without the need to import
# this file. See the following link for more information:
# https://www.tutorialspoint.com/pytest/pytest_conftest_py.htm

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
