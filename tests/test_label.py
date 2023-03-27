import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.core.config import token


def test_get_labels(test_client):
    url = "/v1/label/"
    test_cases = [
        {"token": token, "status_code": 200},
        {"token": None, "status_code": 422},
        {"token": "shoe", "status_code": 401},
    ]
    for case in test_cases:
        param = {"token": case.get("token")}

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
