from datetime import datetime, timedelta

import Config
import pandas as pd
import SQL
from flask import Blueprint, request
from flask.json import jsonify
import utils.string_processing

detect = Blueprint('detect', __name__, template_folder='templates')


@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
@detect.route('/<version>/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(version=None, manual_detect=0):
    detections = request.get_json()
    
    manual_detect = 0 if int(manual_detect) == 0 else 1

    df = pd.DataFrame(detections)
    original_shape = df.shape

    #remove blank rows
    df.dropna(inplace=True)

    # remove duplicates
    df.drop_duplicates(subset=["reporter","reported","region_id"], inplace=True)

    #normalize time values
    df["ts"] = pd.to_datetime(df["ts"], unit='s', utc=True)

    #remove any row with timestamps now within the LAST 24 hours. No future or really old entries.
    now = datetime.utcnow()
    now = pd.to_datetime(now, utc=True)
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday = pd.to_datetime(yesterday, utc=True)

    #create filter for df; only timestamps between now and 24 hours ago
    mask = (df["ts"] >= yesterday) & (df["ts"] <= now)
    df = df[mask]
    cleaned_shape = df.shape

    #Kicks out lists with more than 5k sightings and more than 1 reporter
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        Config.debug(f'too many reports: {df.shape}')
        return jsonify({'OK': 'OK'})
    
    if len(df) == 0:
        Config.debug(f'No valid reports, {original_shape=}, {cleaned_shape=}')
        return jsonify({'OK': 'OK'})

    detections = df.to_dict('records')

    Config.debug(f'      Received detections: DF shape: {df.shape}')
    Config.sched.add_job(process_detections ,args=[detections, manual_detect], replace_existing=False, name='detect', misfire_grace_time=60)

    return jsonify({'OK': 'OK'})


def process_detections(detections, manual_detect: int):

    values_rows = []

    column_names = [
        'reportedID',
        'reportingID',
        'region_id',
        'x_coord',
        'y_coord',
        'z_coord',
        'timestamp',
        'manual_detect',
        'on_members_world',
        'on_pvp_world',
        'world_number',
        'equip_head_id',
        'equip_amulet_id',
        'equip_torso_id',
        'equip_legs_id',
        'equip_boots_id',
        'equip_cape_id',
        'equip_hands_id',
        'equip_weapon_id',
        'equip_shield_id',
        'equip_ge_value'
    ]

    for detection in detections:
        values_rows.append(normalize_detection(detection, manual_detect))

    SQL.insert_multiple_reports(columns=column_names, values=values_rows)

    return


def normalize_detection(detection, manual_detect):

    # input validation
    bad_name = False
    detection['reporter'], bad_name = SQL.name_check(detection['reporter'])
    detection['reported'], bad_name = SQL.name_check(detection['reported'])

    if bad_name:
        Config.debug(f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        return 0

    if  not (0 <= int(detection['region_id']) <= 15522):
        return 0

    if  not (0 <= int(detection['region_id']) <= 15522):
        return 0

    # get reporter & reported
    reporter = SQL.get_player(detection['reporter'])
    reported = SQL.get_player(detection['reported'])

    create = 0
    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = SQL.insert_player(detection['reporter'])

    if reported is None:
        reported = SQL.insert_player(detection['reported'])

    values = []

    values.append(int(reported.id))
    values.append(int(reporter.id))
    values.append(detection.get("region_id"))
    values.append(detection.get("x"))
    values.append(detection.get("y"))
    values.append(detection.get("z"))
    values.append(f"\"{format_timestamp(detection.get('ts'))}\"")
    values.append(manual_detect)
    values.append(detection.get("on_members_world"))
    values.append(detection.get("on_pvp_world"))
    values.append(detection.get("world_number"))
    values.append(detection.get("equipment").get("HEAD"))
    values.append(detection.get("equipment").get("AMULET"))
    values.append(detection.get("equipment").get("TORSO"))
    values.append(detection.get("equipment").get("LEGS"))
    values.append(detection.get("equipment").get("BOOTS"))
    values.append(detection.get("equipment").get("CAPE"))
    values.append(detection.get("equipment").get("HANDS"))
    values.append(detection.get("equipment").get("WEAPON"))
    values.append(detection.get("equipment").get("SHIELD"))
    values.append(detection.get("equipment_ge"))

    values = remove_nones(values)

    values = [str(v) for v in values]

    joined_values = ','.join(values)

    return "(" + joined_values +")"


def remove_nones(values):
    fixed_values = []

    for v in values:
        if v is None:
            fixed_values.append("null")
        else:
            fixed_values.append(v)

    return fixed_values


def format_timestamp(ts):
    dt = ts.to_pydatetime()
    dt = dt.strftime("%Y/%m/%d %H:%M:%S")
    return dt