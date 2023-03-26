import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import token


def test_scraper_players(test_client):
    url = f"/scraper/players/0/10/{token}"
    response = test_client.get(url)

    print(response.url)
    print(response.text)

    # status code check
    status_code = 200
    error = (
        f"Invalid response, Received: {response.status_code}, expected {status_code}"
    )
    assert response.status_code == status_code, error

    # type check
    if response.ok:
        error = f"Invalid response return type, expected list[dict]"
        assert isinstance(response.json(), list), error
