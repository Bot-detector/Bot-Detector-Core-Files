import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import token


def test_get_player_hiscore_data(test_client):
    test_cases = [
        {"player_id": 1, "status_code": 200, "detail": "valid player"},
        {"player_id": -1, "status_code": 422, "detail": "invalid player id"},
        {"player_id": "shoe", "status_code": 422, "detail": "invalid player id"},
        {"player_id": None, "status_code": 422, "detail": "invalid player id"},
    ]

    for case in test_cases:
        url = "/v1/hiscore/"
        param = {"player_id": case.get("player_id"), "token": token}

        response = test_client.get(url, params=param)

        print(response.url)
        print(response.text)
        print(case, param)
        # status code check
        status_code = case.get("status_code")
        error = f"Invalid response, Received: {response.status_code}, expected {status_code}"
        assert response.status_code == status_code, error

        # type check
        if response.ok:
            error = f"Invalid response return type, expected list[dict]"
            assert isinstance(response.json(), list), error


def test_get_latest_hiscore_data_for_an_account(test_client):
    test_cases = [
        {"player_id": 1, "status_code": 200, "detail": "valid player"},
        {"player_id": -1, "status_code": 422, "detail": "invalid player id"},
        {"player_id": "shoe", "status_code": 422, "detail": "invalid player id"},
        {"player_id": None, "status_code": 422, "detail": "invalid player id"},
    ]

    for case in test_cases:
        url = "/v1/hiscore/Latest/"
        param = {"player_id": case.get("player_id"), "token": token}

        response = test_client.get(url, params=param)

        print(response.url)
        print(response.text)
        print(case, param)
        # status code check
        status_code = case.get("status_code")
        error = f"Invalid response, Received: {response.status_code}, expected {status_code}"
        assert response.status_code == status_code, error

        # type check
        if response.ok:
            error = f"Invalid response return type, expected list[dict]"
            assert isinstance(response.json(), list), error


# TODO: cleanup
def test_get_latest_hiscore_data_by_player_features(test_client):
    test_case = (
        (1, 1, 0, 0, 2, 200),  # banned account
        (0, 0, 0, 0, 0, 200),  # normal player
        ("shoe", "shoe", "shoe", "shoe", "shoe", 422),  # nonsense
        (None, None, None, None, None, 422),  # None nonsense
    )

    for test, (
        possible_ban,
        confirmed_ban,
        confirmed_player,
        label_id,
        label_jagex,
        response_code,
    ) in enumerate(test_case):
        route_attempt = f"/v1/hiscore/Latest/bulk?token={token}&row_count=10&page=1&possible_ban={possible_ban}&confirmed_ban={confirmed_ban}&confirmed_player={confirmed_player}&label_id={label_id}&label_jagex={label_jagex}"
        response = test_client.get(route_attempt)
        assert (
            response.status_code == response_code
        ), f"Test: {test}| Invalid response {response.status_code}"
        if response.status_code == 200:
            assert isinstance(
                response.json(), list
            ), f"invalid response return type: {type(response.json())}"


def test_get_account_hiscore_xp_change(test_client):
    test_cases = [
        {"player_id": 1, "status_code": 200, "detail": "valid player"},
        {"player_id": -1, "status_code": 422, "detail": "invalid player id"},
        {"player_id": "shoe", "status_code": 422, "detail": "invalid player id"},
        {"player_id": None, "status_code": 422, "detail": "invalid player id"},
    ]

    for case in test_cases:
        url = "/v1/hiscore/XPChange"
        param = {"player_id": case.get("player_id"), "token": token}

        response = test_client.get(url, params=param)

        print(response.url)
        print(response.text)
        print(case, param)
        # status code check
        status_code = case.get("status_code")
        error = f"Invalid response, Received: {response.status_code}, expected {status_code}"
        assert response.status_code == status_code, error

        # type check
        if response.ok:
            error = f"Invalid response return type, expected list[dict]"
            assert isinstance(response.json(), list), error


if __name__ == "__main__":
    """get tests"""
    test_get_player_hiscore_data()
    test_get_latest_hiscore_data_for_an_account()
    test_get_latest_hiscore_data_by_player_features()
    test_get_account_hiscore_xp_change()

    """post tests"""
    # test_post_hiscore()
