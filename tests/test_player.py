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
    
    for player_name, player_id, response_code in test_case:
      route_attempt = f"/v1/player?token={token}&player_name={player_name}&player_id={player_id}&row_count=100000&page=1"
      response = client.get(route_attempt)
      assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
      if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'


"""
  Players post routes
"""
## DUPLICATE ENTRIES ON DEV
def test_post_player():
    test_case = (
      ('ferrariic', 200), # correct name, and correct ID 
      (8, 422), #juxtaposed player_id and player_name
      (None, 422), # None entry
    )
    for player_name, response_code in test_case:
        route_attempt = f'/v1/player?player_name={player_name}&token={token}'
        response = client.get(url=route_attempt)
        assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
        
        
if __name__ == "__main__":
  '''get route'''
  test_get_player_information()

  '''post route'''
  test_post_player()