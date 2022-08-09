import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from fastapi.testclient import TestClient

client = TestClient(app.app)

def test_get_feedback():
    url = "/v1/feedback/count/"
    test_cases = [
        {"name":"3BA604236FB0319D5937E31388B0C64C", "status_code": 200}
    ]
    for case in test_cases:
        param = {"name": case.get("name")}

        response = client.get(url, params=param)

        print(response.url)
        print(response.text)
        print(case, param)
        # status code check
        status_code = case.get("status_code")
        error = f"Invalid response, Received: {response.status_code}, expected {status_code}, {case}"
        assert response.status_code == status_code, error

        # type check
        if response.ok:
            error = f"Invalid response return type, expected list[dict]"
            assert isinstance(response.json(), list), error
