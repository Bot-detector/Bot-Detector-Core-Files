from os import name
import re
import time
from datetime import datetime, timedelta

from sqlalchemy.util.langhelpers import NoneType

import Config
import pandas as pd
import SQL
from flask import Blueprint, request
from flask.json import jsonify

detect = Blueprint('detect', __name__, template_folder='templates')

def is_valid_rsn(rsn):
    return re.fullmatch('[\w\d\s_-]{1,13}', rsn)

def to_jagex_name(name: str) -> str:
    return name.lower().replace('_', ' ').replace('-',' ').strip()

def sql_select_players(names):
    sql = "SELECT * FROM Players WHERE name in :names"
    param = {'names': names}
    data = SQL.execute_sql(sql, param, has_return=True)
    return data

def parse_detection(data:dict) ->dict:
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    equipment = data.get('equipment')

    param = {
        'reportedID': data.get('id'),
        'reportingID': data.get('reporter_id'),
        'region_id': data.get('region_id'),
        'x_coord': data.get('x'),
        'y_coord': data.get('y'),
        'z_coord': data.get('z'),
        'timestamp': human_time,
        'manual_detect': data.get('manual_detect'),
        'on_members_world': data.get('on_members_world'),
        'on_pvp_world': data.get('on_pvp_world'),
        'world_number': data.get('world_number'),
        'equip_head_id': equipment.get('HEAD'),
        'equip_amulet_id': equipment.get('AMULET'),
        'equip_torso_id': equipment.get('TORSO'),
        'equip_legs_id': equipment.get('LEGS'),
        'equip_boots_id': equipment.get('BOOTS'),
        'equip_cape_id': equipment.get('CAPE'),
        'equip_hands_id': equipment.get('HANDS'),
        'equip_weapon_id': equipment.get('WEAPON'),
        'equip_shield_id': equipment.get('SHIELD'),
        'equip_ge_value': data.get('equipment_ge')
    }
    return param

def process_data(df, names, manual_detect):
    # 1) Ensure names are valid
    valid_names = [name for name in names if is_valid_rsn(name)]

    # 2) Get IDs for all unique names
    data = sql_select_players(valid_names)
    
    # 3) Create entries for players that do not yet exist in Players table
    existing_names = [d.name for d in data]
    new_names = set(valid_names).difference(existing_names)
    
    # 3.1) Get those players' IDs from step 3
    if new_names:
        sql = "insert ignore into Players (name, normalized_name) values (:name, :normalized_name)"
        param = [{"name": name, "normalized_name": to_jagex_name(name)} for name in new_names]
        SQL.execute_sql(sql, param, has_return=False)

        data.extend(sql_select_players(new_names))

    # 4) Insert detections into Reports table with user ids 
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)
    df = df.merge(df_names, left_on="reported", right_on="name")
    
    df["reporter_id"]  = df_names.query(f"name == {df['reporter'].unique()}")['id'].to_list()[0]

    df['manual_detect'] = manual_detect
    # 4.2) parse data to param
    data = df.to_dict('records')
    param = [parse_detection(d) for d in data]
    # 4.3) parse query
    params = list(param[0].keys())
    columns = SQL.list_to_string(params)
    values = SQL.list_to_string([f':{column}' for column in params])

    sql = f'insert ignore into Reports ({columns}) values ({values})'
    SQL.execute_sql(sql, param, has_return=False)
    return

@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
@detect.route('/<version>/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(version=None, manual_detect=0):
    # parse input
    detections = request.get_json()
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame(detections)
    df.drop_duplicates(subset=['reporter', 'reported', 'region_id'], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        Config.debug('to many reports')
        return {'OK': 'OK'}

    Config.debug(f"Received: {len(df)} from: {df['reporter'].unique()}")

    # 1) Get a list of unqiue reported names and reporter name 
    names = list(df['reported'].unique())
    names.extend(df['reporter'].unique())

    Config.sched.add_job(
        process_data, args=[df, names, manual_detect], name='detect' , misfire_grace_time=None, replace_existing=False
    )
    return {'OK': 'OK'}
