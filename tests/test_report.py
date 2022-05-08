import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

def test_report_count():
    url = "/v1/report/count"
    test_cases = [
        {"name": "extreme4all", "status_code": 200},
        {"name": None, "status_code": 422},
    ]
    for case in test_cases:
        param = {"token": token, "name": case.get("name")}

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