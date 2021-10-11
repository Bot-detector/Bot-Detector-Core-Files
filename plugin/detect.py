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
    Config.sched.add_job(process_detections ,args=[detections, manual_detect], replace_existing=False, name='detect', misfire_grace_time=None)

    return jsonify({'OK': 'OK'})


def process_detections(detections, manual_detect: int):
    '''
        create a list of dict with keys that match the db columns
    '''
    data = [normalize_detection(d, manual_detect) for d in detections]
    SQL.insert_report(data)
    return


def normalize_detection(detection, manual_detect):
    # input validation
    detection['reporter'], bad_name_reporter = SQL.name_check(detection['reporter'])
    detection['reported'], bad_name_reported = SQL.name_check(detection['reported'])

    if bad_name_reporter or bad_name_reported:
        Config.debug(f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        return

    if  not (0 <= int(detection['region_id']) <= 15522):
        return

    if  not (0 <= int(detection['region_id']) <= 15522):
        return

    # get reporter & reported
    reporter = SQL.get_player(detection['reporter'])
    reported = SQL.get_player(detection['reported'])

    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = SQL.insert_player(detection['reporter'])

    if reported is None:
        reported = SQL.insert_player(detection['reported'])

    data = {
        'reportedID': int(reported.id),
        'reportingID': int(reporter.id),
        'region_id': detection.get('region_id'),
        'x_coord': detection.get('x'),
        'y_coord': detection.get('y'),
        'z_coord': detection.get('z'),
        'timestamp': detection.get('ts'),
        'manual_detect': manual_detect,
        'on_members_world': detection.get('on_members_world'),
        'on_pvp_world': detection.get('on_pvp_world'),
        'world_number': detection.get('world_number'),
        'equip_head_id': detection.get('equipment').get('HEAD'),
        'equip_amulet_id': detection.get('equipment').get('AMULET'),
        'equip_torso_id': detection.get('equipment').get('TORSO'),
        'equip_legs_id': detection.get('equipment').get('LEGS'),
        'equip_boots_id': detection.get('equipment').get('BOOTS'),
        'equip_cape_id': detection.get('equipment').get('CAPE'),
        'equip_hands_id': detection.get('equipment').get('HANDS'),
        'equip_weapon_id': detection.get('equipment').get('WEAPON'),
        'equip_shield_id': detection.get('equipment').get('SHIELD') ,
        'equip_ge_value': detection.get('equipment_ge')
    }
    return data