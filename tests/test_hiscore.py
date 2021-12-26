import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Hiscore get routes
"""
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_player_hiscore_data():
  
    test_case = (
      (-1, 200), # invalid player id
      (1, 200), # valid player id
      (8, 200), # valid player id
      ('shoe', 422), # invalid entry type
      (None, 422), # none entry type
      )
    
    for player_id, response_code in test_case:
      route_attempt = f"/v1/hiscore/?player_id={player_id}&token={token}"
      response = client.get(route_attempt)
      assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
      if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

def test_get_latest_hiscore_data_for_an_account():
  
    test_case = (
      (-1, 200), # invalid player id
      (1, 200), # valid player id
      (8, 200), # valid player id
      ('shoe', 422), # invalid entry type
      (None, 422), # none entry type
      )
    
    for player_id, response_code in test_case:
      route_attempt = f"/v1/hiscore/Latest?token={token}&player_id={player_id}"
      response = client.get(route_attempt)
      assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
      if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
    
def test_get_latest_hiscore_data_by_player_features():
  
  test_case = (
    (1,1,0,0,2, 200), # banned account
    (0,0,0,0,0, 200), # normal player
    ('shoe','shoe','shoe','shoe','shoe', 422), # nonsense
    (None, None, None, None, None, 422), # None nonsense
    )
  
  for possible_ban, confirmed_ban, confirmed_player, label_id, label_jagex, response_code in test_case:
    route_attempt = f"/v1/hiscore/Latest/bulk?token={token}&row_count=10&page=1&possible_ban={possible_ban}&confirmed_ban={confirmed_ban}&confirmed_player={confirmed_player}&label_id={label_id}&label_jagex={label_jagex}"
    response = client.get(route_attempt)
    assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
    if response.status_code == 200:
      assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
  
def test_get_account_hiscore_xp_change():
  response = client.get(f"")
  
  test_case = (
    (-1, 200), # invalid player id
    (1, 200), # valid player id
    (8, 200), # valid player id
    ('shoe', 422), # invalid entry type
    (None, 422), # none entry type
    )
  for player_id, response_code in test_case:
    response = client.get(f"/v1/hiscore/XPChange?token={token}&player_id={player_id}&row_count=1&page=1")
    assert response.status_code == response_code, f'invalid response {response.status_code}'
    if response.status_code == 200:
      assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

if __name__ == '__main__':
  """
    Hiscore get tests
  """
  test_get_player_hiscore_data()
  test_get_latest_hiscore_data_for_an_account()
  test_get_latest_hiscore_data_by_player_features()
  test_get_account_hiscore_xp_change()