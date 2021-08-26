import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from fastapi.testclient import TestClient

client = TestClient(app.app)

def test_hiscore():
    response = client.get("/v1/hiscore/?player_name=extreme4all")
    assert response.status_code == 200, f'invalid response {response.status_code }'
    assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'


if __name__ == "__main__":
  test_hiscore()
