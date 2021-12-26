import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Prediction get routes
"""

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_account_prediction_result():
  
    test_case = (
      ('ferrariic', 200), # correct name, and correct ID 
      (';a;jj', 200), # nonsense
      (';a;jjaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 200), # nonsense
      (';a;jj$$@##@#@', 200), # nonsense
      ('', 200), # nonsense
      (None, 200), # None entry
    )
    
    for player_name, response_code in test_case:
      route_attempt = f"/v1/prediction?token={token}&name={player_name}"
      response = client.get(route_attempt)
      assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
      if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

def test_gets_predictions_by_player_features():
  
  test_case = (
    (1,1,0,0,2, 200), # banned account
    (0,0,0,0,0, 200), # normal player
    (-1,0,0,0,0, 422), # invalid value
    (0,-1,0,0,0, 422), # invalid value
    (0,0,-1,0,0, 422), # invalid value
    (0,0,0,-1,0, 422), # invalid value
    (0,0,0,0,-1, 422), # invalid value
    (2,0,0,0,0, 422), # invalid value
    (0,2,0,0,0, 422), # invalid value
    (0,0,2,0,0, 422), # invalid value
    (0,0,0,2,0, 422), # invalid value
    (0,0,0,0,2, 422), # invalid value
    ('shoe','shoe','shoe','shoe','shoe', 422), # nonsense
    (None, None, None, None, None, 422), # None entry
    )
  for possible_ban, confirmed_ban, confirmed_player, label_id, label_jagex, response_code in test_case:
    route_attempt = f"/v1/prediction/bulk?token={token}&row_count=100000&page=1&possible_ban={possible_ban}&confirmed_ban={confirmed_ban}&confirmed_player={confirmed_player}&label_id={label_id}&label_jagex={label_jagex}"
    response = client.get(route_attempt)
    assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
    if response.status_code == 200:
        assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

def test_get_expired_predictions():
  
    test_case = (
      (-1, 422), # invalid limit
      (0, 422), # zero limit
      (1, 200), # valid limit
      (None, 422), # None entry
    )
    
    for limit, response_code in test_case:
        route_attempt = f"/v1/prediction/data?token={token}&limit={limit}"
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'


"""
  Prediction post routes
"""

if __name__ == "__main__":
  '''get routes'''
  test_get_account_prediction_result()
  test_gets_predictions_by_player_features()
  test_get_expired_predictions()
  
  '''post routes'''

