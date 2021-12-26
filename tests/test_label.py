import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Labels get routes
"""

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_labels_from_plugin_database():
  
    test_case = (
      (None, 401), # no token
      (token, 200), # correct token
      ('shoe', 401), # invalid token
    )
    
    for test_token, response_code in test_case:
        route_attempt = f'/v1/label/?token={test_token}'
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

if __name__ == "__main__":
  test_get_labels_from_plugin_database()
