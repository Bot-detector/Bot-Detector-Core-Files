import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time

from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

def test_scraper_players():
    url = f"/scraper/players/0/10/{token}"
    response = client.get(url)

    print(response.url)
    print(response.text)
    
    # status code check
    status_code = 200
    error = f"Invalid response, Received: {response.status_code}, expected {status_code}"
    assert response.status_code == status_code, error

    # type check
    if response.ok:
        error = f"Invalid response return type, expected list[dict]"
        assert isinstance(response.json(), list), error