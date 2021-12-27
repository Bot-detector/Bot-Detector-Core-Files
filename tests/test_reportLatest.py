import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from json_post_test_cases import post_report_test_case

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Report get routes
"""

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_reportLatest_from_plugin_database():
  
    test_case = (
      (1, 12598, 200), # correct
      (-1, 12598, 422), # impossible reported id
      (1, -1, 422), # impossible region id
      (1, 20000000, 422), # out of range region_id
    )
    
    for test, (reported_id, region_id, response_code) in enumerate(test_case):
        route_attempt = f'/v1/reportLatest?token={token}&reported_id={reported_id}&regionID={region_id}'
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'Test: {test} | Invalid response {response.status_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
    

if __name__ == "__main__":
  '''get route'''
  test_get_reportLatest_from_plugin_database()