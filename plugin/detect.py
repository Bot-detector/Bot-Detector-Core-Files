from flask import Blueprint, request
from flask.json import jsonify
import SQL, Config
import concurrent.futures as cf
import pandas as pd
import sys
import logging

detect = Blueprint('detect', __name__, template_folder='templates')

def custom_hiscore(detection):

    # get reporter & reported
    reporter = SQL.get_player(detection['reporter'])
    reported = SQL.get_player(detection['reported'])

    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = SQL.insert_player(detection['reporter'])

    if reported is None:
        reported = SQL.insert_player(detection['reported'])

    # change in detection
    detection['reported'] = reported.id
    detection['reporter'] = reporter.id

    # insert into reports
    SQL.insert_report(detection)


def insync_detect(detections, manual_detect):
    for idx, detection in enumerate(detections):
        detection['manual_detect'] = manual_detect
        custom_hiscore(detection)
        if idx % 100 == 0 and idx != 0:
            logging.debug(msg=f'      Completed {idx}/{len(detections)}')

    logging.debug(msg=f'      Done: Completed {idx} detections')


@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(manual_detect=0):
    detections = request.get_json()
    manual_detect = 0 if int(manual_detect) == 0 else 1
    # remove duplicates
    df = pd.DataFrame(detections)
    df.drop_duplicates(subset=['reporter','reported','region_id'], inplace=True)
    
    detections = df.to_dict('records')

    logging.debug(msg=f'      Received detections: DF shape: {df.shape}')
    Config.sched.add_job(lambda: insync_detect(detections, manual_detect), replace_existing=False, name='detect')

    return jsonify({'OK': 'OK'})
