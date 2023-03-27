import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.core.config import token


def test_report_count(test_client):
    url = "/v1/report/count"
    test_cases = [
        {"name": "3BA604236FB0319D5937E31388B0C64C", "status_code": 200},
        {"name": None, "status_code": 422},
    ]
    for case in test_cases:
        param = {"token": token, "name": case.get("name")}

        response = test_client.get(url, params=param)

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
