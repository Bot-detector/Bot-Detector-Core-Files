'''
This file should hold all the tests for the legacy routes (routers/legacy.py)
https://fastapi.tiangolo.com/tutorial/testing/
'''
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)


def test_detect():
    version = "test"
    manual_detect = 0

    formatted_detection = [{
        "reporter": "m5ppKBSk1lCiC",
        "reported": "nt7Si4pCsE0va",
        "region_id": 0,
        "x": 0,
        "y": 0,
        "z": 0,
        "ts": 1636478642,
        "on_members_world": 0,
        "on_pvp_world": 0,
        "world_number": 0,
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
        "equip_ge_value": 123
    }]

    response = client.post(url=f"/{version}/plugin/detect/{manual_detect}", json=formatted_detection)

    assert response.status_code == 200, f'invalid response {response.status_code }'
    assert isinstance(response.json(), dict), f'invalid response return type: {type(response.json())}'


def test_get_prediction():
    version = "test"
    player_names = [("this_is_bad", 200), ("testing", 200), ("Seltzer Bro", 200), ("a;d;5230fadgkas", 400)]

    for name in player_names:
        response = client.get(f"/{version}/site/prediction/{name[0]}")
        print(type(response))
        assert response.status_code == name[1], f'invalid response {response.status_code }'


if __name__ == "__main__":
  test_get_prediction()
