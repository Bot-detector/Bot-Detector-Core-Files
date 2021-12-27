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
def test_get_reports_from_plugin_database():
  
    test_case = (
      (1, 8, 12598, 200), # correct
      ('ferrariic', 8, 12598, 422), # malformed entry
      (1, 'ferrariic', 12598, 422), # malformed entry
      (1, 8, -1, 422), # -1 region
      (-1, 8, -1, 422), # -1 value
      (1, -8, -1, 422), # -1 value
      (0, 0, 12598, 200), # same reporter id (invalid)
      (8, 8, 12598, 200), # same reporter id (valid)
      (1, 8, 'varrock', 422), # malformed entry
      (None, None, None, 422), # none fields
    )
    
    for reported_id, reporting_id, region_id, response_code in test_case:
        route_attempt = f'/v1/report?token={token}&reportedID={reported_id}&reportingID={reporting_id}&regionID={region_id}'
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
            
"""
  Report post routes
"""

def test_post_report():
    for test, (payload, response_code) in enumerate(post_report_test_case):
        route_attempt = f'/v1/report/?token={token}'
        response = client.post(url=route_attempt, json=payload)
        assert response.status_code == response_code, f'Test: {test} | Invalid response {response.status_code}'

if __name__ == "__main__":
  '''get route'''
  test_get_reports_from_plugin_database()

  '''post route'''
  test_post_report()