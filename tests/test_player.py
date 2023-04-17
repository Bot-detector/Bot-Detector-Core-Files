import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import token


def test_get_player_information(test_client):
    test_cases = [
        {"player_id": 1, "status_code": 200, "detail": "valid player"},
        {"player_id": -1, "status_code": 422, "detail": "invalid player id"},
        {"player_id": "shoe", "status_code": 422, "detail": "invalid player id"},
        {"player_id": None, "status_code": 422, "detail": "invalid player id"},
    ]

    for case in test_cases:
        url = "/v1/player/"
        param = {"player_id": case.get("player_id"), "token": token}

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
