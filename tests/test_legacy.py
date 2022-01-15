import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import time

from api import app
from fastapi.testclient import TestClient

client = TestClient(app.app)


post_report_test_case = (
        ([
            {
                "reporter": "Ferrariic", # correct name
                "reported": "extreme4all", # correct name
                "region_id": 12598,
                "x": 10,
                "y": 10,
                "z": 10,
                "ts": int(time.time()),
                "on_members_world": 1,
                "on_pvp_world": 0,
                "world_number": 330,
                "equipment": {
                    "HEAD": 0,
                    "AMULET": 0,
                    "TORSO": 0,
                    "LEGS": 0,
                    "BOOTS": 0,
                    "CAPE": 0,
                    "HANDS": 0,
                    "WEAPON": 0,
                    "SHIELD": 0
                },
                "equipment_ge": 0
            }
        ], '1.3.7.2', 0, 200),
        ([
            {
                "reporter": "ferrariic", # correct name
                "reported": "extreme4all", # correct name
                "region_id": 12598,
                "x": 10,
                "y": 10,
                "z": 10,
                "ts": int(time.time()),
                "on_members_world": 1,
                "on_pvp_world": 0,
                "world_number": 330,
                "equipment": {
                    "HEAD": 0,
                    "AMULET": 0,
                    "TORSO": 0,
                    "LEGS": 0,
                    "BOOTS": 0,
                    "CAPE": 0,
                    "HANDS": 0,
                    "WEAPON": 0,
                    "SHIELD": 0
                },
                "equipment_ge": 0
            }
        ], '1.3.7.2', 0, 200),
        ([
            {
                "reporter": "ferrariic", # correct name
                "reported": "Extreme4all", # correct name
                "region_id": 12598,
                "x": 10,
                "y": 10,
                "z": 10,
                "ts": int(time.time()),
                "on_members_world": 1,
                "on_pvp_world": 0,
                "world_number": 330,
                "equipment": {
                    "HEAD": 0,
                    "AMULET": 0,
                    "TORSO": 0,
                    "LEGS": 0,
                    "BOOTS": 0,
                    "CAPE": 0,
                    "HANDS": 0,
                    "WEAPON": 0,
                    "SHIELD": 0
                },
                "equipment_ge": 0
            }
        ], '1.3.7.2', 0, 200),
        ([
            {
                "reporter": "FERRARIIC", # correct name
                "reported": "EXTREME4ALL", # correct name
                "region_id": 12598,
                "x": 10,
                "y": 10,
                "z": 10,
                "ts": int(time.time()),
                "on_members_world": 1,
                "on_pvp_world": 0,
                "world_number": 330,
                "equipment": {
                    "HEAD": 0,
                    "AMULET": 0,
                    "TORSO": 0,
                    "LEGS": 0,
                    "BOOTS": 0,
                    "CAPE": 0,
                    "HANDS": 0,
                    "WEAPON": 0,
                    "SHIELD": 0
                },
                "equipment_ge": 0
            }
        ], '1.3.7.2', 0, 200),
    )

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_post_report():
    for test, (payload, version, manual_detect, response_code) in enumerate(post_report_test_case):
        route_attempt = f'/{version}/plugin/detect/{manual_detect}'
        response = client.post(url=route_attempt, json=payload)
        assert response.status_code == response_code, f'Test: {test}, Invalid response: {response.status_code}, expected: {response_code}'

# @pytest.mark.filterwarnings('ignore::DeprecationWarning')
# def test_get_reports_from_plugin_database():
  
#     test_case = (
#       (1, 8, 12598, 200), # correct
#       ('ferrariic', 8, 12598, 422), # malformed entry
#       (1, 'ferrariic', 12598, 422), # malformed entry
#       (1, 8, -1, 422), # -1 region
#       (-1, 8, -1, 422), # -1 value
#       (1, -8, -1, 422), # -1 value
#       (0, 0, 12598, 200), # same reporter id (invalid)
#       (8, 8, 12598, 200), # same reporter id (valid)
#       (1, 8, 'varrock', 422), # malformed entry
#       (None, None, None, 422), # none fields
#     )
    
#     for test, (reported_id, reporting_id, region_id, response_code) in enumerate(test_case):
#         route_attempt = f'/v1/report?token={token}&reportedID={reported_id}&reportingID={reporting_id}&regionID={region_id}'
#         response = client.get(route_attempt)
#         assert response.status_code == response_code, f'Test: {test}, Invalid response {response.status_code}, expected: {response_code}'
#         if response.status_code == 200:
#             assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
            
            
if __name__ == "__main__":
    test_post_report()
