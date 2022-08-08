import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)


def test_prediction():
    url = "/v1/prediction/"
    test_cases = [
        # test name string check
        {"name": None, "status_code": 422},
        # test default breakdown
        {"name": "3BA604236FB0319D5937E31388B0C64C", "status_code": 200},
        # test breakdown true
        {
            "name": "2C09003E9EA22E5F245023B5555C0AD9",
            "breakdown": True,
            "status_code": 200,
        },
        # test breakdown false
        {
            "name": "2C09003E9EA22E5F245023B5555C0AD9",
            "breakdown": False,
            "status_code": 200,
        },
    ]
    for case in test_cases:
        param = {
            "token": token,
            "name": case.get("name"),
        }
        if case.get("breakdown"):
            param["breakdown"] = case.get("breakdown")

        response = client.get(url, params=param)

        # status code check
        status_code = case.get("status_code")
        error = f"Invalid response, Received: {response.status_code}, expected {status_code}, {case}"
        assert response.status_code == status_code, error

        # type check
        if response.ok:
            error = f"Invalid response return type, expected list[dict]"
            data: dict = response.json()
            assert isinstance(data, dict), error

        if case.get("breakdown"):
            assert data.get("predictions_breakdown") is not None, "expected a breakdown"
