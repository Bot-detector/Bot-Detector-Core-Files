import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Player get routes
"""

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_player_information():
    test_case = (
      ('ferrariic', 8, 200), # correct name, and correct ID 
      ('ferrariic', -8, 422), # correct name, incorrect ID
      (1,'ferrariic', 422), #juxtaposed player_id and player_name
      ('shoe','shoe', 422), #invalid phrasing
      (None, None, 422), # None entry
    )
    
    for test, (player_name, player_id, response_code) in enumerate(test_case):
      route_attempt = f"/v1/player?token={token}&player_name={player_name}&player_id={player_id}&row_count=100000&page=1"
      response = client.get(route_attempt)
      assert response.status_code == response_code, f'Test: {test} | Invalid response {response.status_code}'
      if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'


"""
  Players post routes
"""

if __name__ == "__main__":
  '''get route'''
  test_get_player_information()

  '''post route'''