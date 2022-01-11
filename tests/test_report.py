import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Report get routes
"""
post_report_test_case = ((
    [{
        "reporter": "Ferrariic",
        "reported": "fejfeaeafe",
        "region_id": 28,
        "x_coord": 10,
        "y_coord": 10,
        "z_coord": 10,
        "ts": int(time.time())-1,
        "manual_detect": 0,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 302,
        "equipment": {
            "equip_head_id": 0,
            "equip_amulet_id": 0,
            "equip_torso_id": 0,
            "equip_legs_id": 0,
            "equip_boots_id": 0,
            "equip_cape_id": 0,
            "equip_hands_id": 0,
            "equip_weapon_id": 0,
            "equip_shield_id": 0
        },
        "equip_ge_value": 0
    }], 201),
    ([{
        "reporter": "Ferrariic",
        "reported": 1,  # id not str, might pass as 200 considering that the player can have a name of '1'
        "region_id": 28,
        "x_coord": 10,
        "y_coord": 10,
        "z_coord": 10,
        "ts": int(time.time()),
        "manual_detect": 0,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 302,
        "equipment": {
            "equip_head_id": 0,
            "equip_amulet_id": 0,
            "equip_torso_id": 0,
            "equip_legs_id": 0,
            "equip_boots_id": 0,
            "equip_cape_id": 0,
            "equip_hands_id": 0,
            "equip_weapon_id": 0,
            "equip_shield_id": 0
        },
        "equip_ge_value": 0
    }], 201),
    ([{
        "reporter": "Ferrariic",
        "reported": "fejfeaeafe",
        "region_id": 28,
        "x_coord": 10,
        "y_coord": 10,
        "z_coord": 10,
        "ts": -238432,  # negative time
        "manual_detect": 0,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 302,
        "equipment": {
            "equip_head_id": 0,
            "equip_amulet_id": 0,
            "equip_torso_id": 0,
            "equip_legs_id": 0,
            "equip_boots_id": 0,
            "equip_cape_id": 0,
            "equip_hands_id": 0,
            "equip_weapon_id": 0,
            "equip_shield_id": 0
        },
        "equip_ge_value": 0
    }], 422),
    ([{
        "reporter": "Ferrariic",
        "reported": "fejfeaeafe",
        "region_id": 28,
        "x_coord": 10,
        "y_coord": 10,
        "z_coord": 10,
        "ts": int(time.time()),
        "manual_detect": 0,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 302,
        "equipment": {
            "equip_head_id": 0,
            "equip_amulet_id": 0,
            "equip_torso_id": 0,
            "equip_legs_id": 0,
            "equip_boots_id": 0,
            "equip_cape_id": 0,
            "equip_hands_id": 0,
            "equip_weapon_id": 0,
            "equip_shield_id": 0
        },
        "equip_ge_value": 10000000000000000000000  # massive gold
    }], 422),
    ([{
        "reporter": "Ferrariic",
        "reported": "fejfeaeafe",
        "region_id": 28,
        "x_coord": 10,
        "y_coord": 10,
        "z_coord": 10,
        "ts": int(time.time()),
        "manual_detect": 0,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 302,
        "equipment": {
            "equip_head_id": 0,
            "equip_amulet_id": 0,
            "equip_torso_id": 0,
            "equip_legs_id": 0,
            "equip_boots_id": 0,
            "equip_cape_id": 0,
            "equip_hands_id": 0,
            "equip_weapon_id": 0,
            "equip_shield_id": 0
        },
        "equip_ge_value": 0
    },
        {
        "reporter": "Ferrariic2",  # impossible multiple reporters
        "reported": "fejfeaeafe",
            "region_id": 28,
            "x_coord": 10,
            "y_coord": 10,
            "z_coord": 10,
            "ts": int(time.time()),
            "manual_detect": 0,
            "on_members_world": 0,
            "on_pvp_world": 0,
            "world_number": 302,
            "equipment": {
                "equip_head_id": 0,
                "equip_amulet_id": 0,
                "equip_torso_id": 0,
                "equip_legs_id": 0,
                "equip_boots_id": 0,
                "equip_cape_id": 0,
                "equip_hands_id": 0,
                "equip_weapon_id": 0,
                "equip_shield_id": 0
            },
        "equip_ge_value": 0
    }], 400),
)


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
    
    for test, (reported_id, reporting_id, region_id, response_code) in enumerate(test_case):
        route_attempt = f'/v1/report?token={token}&reportedID={reported_id}&reportingID={reporting_id}&regionID={region_id}'
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'Test: {test}, Invalid response {response.status_code}, expected: {response_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'
            
"""
  Report post routes
"""
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_post_report():
    for test, (payload, response_code) in enumerate(post_report_test_case):
      route_attempt = f'/v1/report?manual_detect=0'
      response = client.post(url=route_attempt, json=payload)
      assert response.status_code == response_code, f'Test: {test}, Invalid response: {response.status_code}, expected: {response_code}'

if __name__ == "__main__":
  '''get route'''
  # test_get_reports_from_plugin_database()

  '''post route'''
  test_post_report()
