import time

import Config
import pandas as pd
import SQL
from fastapi import APIRouter
from database.functions import execute_sql, list_to_string

from pydantic import BaseModel
from typing import List

class equipment(BaseModel):
	equip_head_id: int
	equip_amulet_id: int
	equip_torso_id: int
	equip_legs_id: int
	equip_boots_id: int
	equip_cape_id: int
	equip_hands_id: int
	equip_weapon_id: int
	equip_shield_id: int

class detection(BaseModel):
	reportedID: int
	reportingID: int
	region_id: int
	x_coord: int
	y_coord: int
	z_coord: int
	ts: int
	manual_detect: int
	on_members_world: int
	on_pvp_world: int
	world_number: int
	equipment: List[equipment]
	equip_ge_value: int

class detections(BaseModel):
    detections: List[detection] = list

router = APIRouter()

def name_check(name):
    bad_name = False
    if len(name) > 13:
        bad_name = True

    temp_name = name
    temp_name = temp_name.replace(' ', '')
    temp_name = temp_name.replace('_', '')
    temp_name = temp_name.replace('-', '')

    if not (temp_name.isalnum()):
        bad_name = True

    return name, bad_name

def get_player(player_name):
    sql_player_id = 'select * from Players where name = :player_name;'

    param = {
        'player_name': player_name
    }

    # returns a list of players
    player = execute_sql(sql_player_id, param=param, debug=False)

    player_id = None if len(player) == 0 else player[0]

    return player_id

def insert_player(player_name):
    sql_insert = "insert ignore into Players (name) values(:player_name);"

    param = {
        'player_name': player_name
    }

    execute_sql(sql_insert, param=param, debug=False)
    player = get_player(player_name)
    return player

def insert_report(data):
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    param = {
        'reportedID': data.get('reported'),
        'reportingID': data.get('reporter'),
        'region_id': data.get('region_id'),
        'x_coord': data.get('x'),
        'y_coord': data.get('y'),
        'z_coord': data.get('z'),
        'timestamp': human_time,
        'manual_detect': data.get('manual_detect'),
        'on_members_world': data.get('on_members_world'),
        'on_pvp_world': data.get('on_pvp_world'),
        'world_number': data.get('world_number'),
        'equip_head_id': data.get('equipment').get('HEAD'),
        'equip_amulet_id': data.get('equipment').get('AMULET'),
        'equip_torso_id': data.get('equipment').get('TORSO'),
        'equip_legs_id': data.get('equipment').get('LEGS'),
        'equip_boots_id': data.get('equipment').get('BOOTS'),
        'equip_cape_id': data.get('equipment').get('CAPE'),
        'equip_hands_id': data.get('equipment').get('HANDS'),
        'equip_weapon_id': data.get('equipment').get('WEAPON'),
        'equip_shield_id': data.get('equipment').get('SHIELD') ,
        'equip_ge_value': data.get('equipment_ge')
    }

    # list of column values
    columns = list_to_string(list(param.keys()))
    values = list_to_string([f':{column}' for column in list(param.keys())])

    sql_insert = f'insert ignore into Reports ({columns}) values ({values});'
    execute_sql(sql_insert, param=param, debug=False)
    return

def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection['reporter'], bad_name = name_check(detection['reporter'])
    detection['reported'], bad_name = name_check(detection['reported'])

    if bad_name:
        Config.debug(f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        return 0

    if  not (0 <= int(detection['region_id']) <= 15522):
        return 0

    if  not (0 <= int(detection['region_id']) <= 15522):
        return 0

    # get reporter & reported
    reporter = get_player(detection['reporter'])
    reported = get_player(detection['reported'])

    create = 0
    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = insert_player(detection['reporter'])
        create += 1

    if reported is None:
        reported = insert_player(detection['reported'])
        create += 1


    # change in detection
    detection['reported'] = int(reported.id)
    detection['reporter'] = int(reporter.id)

    # insert into reports
    SQL.insert_report(detection)
    return create

def insync_detect(detections, manual_detect):
    print("NSYNC")
    total_creates = 0
    for idx, detection in enumerate(detections):
        detection['manual_detect'] = manual_detect

        total_creates += custom_hiscore(detection)

        if len(detection) > 1000 and total_creates/len(detections) > .75:
            print(f'    Malicious: sender: {detection["reporter"]}')
            Config.debug(f'    Malicious: sender: {detection["reporter"]}')
            break

        if idx % 500 == 0 and idx != 0:
            Config.debug(f'      Completed {idx + 1}/{len(detections)}')

    Config.debug(f'      Done: Completed {idx + 1} detections')

# @router.route('/plugin/detect/<manual_detect>', methods=['POST'])
@router.route('/{version}/plugin/detect/{manual_detect}', methods=['POST'])
def post_detect(detections:detection, version: str=None, manual_detect:int=0):
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame(detections)
    df.drop_duplicates(subset=['reporter','reported','region_id'], inplace=True)

    if len(df) > 5000 or df["reporter"].nunique() > 1:
        print('to many reports')
        Config.debug('to many reports')

        return {'NOK': 'NOK'}, 400
    
    detections = df.to_dict('records')

    print(f'      Received detections: DF shape: {df.shape}')

    Config.debug(f'      Received detections: DF shape: {df.shape}')
    Config.sched.add_job(insync_detect ,args=[detections, manual_detect], replace_existing=False, name='detect')
    return {'OK': 'OK'}
