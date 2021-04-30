from flask import Blueprint, request
from flask.json import jsonify
import SQL, Config
import pandas as pd

detect = Blueprint('detect', __name__, template_folder='templates')

def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection['reporter'], bad_name = SQL.name_check(detection['reporter'])
    detection['reported'], bad_name = SQL.name_check(detection['reported'])

    if bad_name:
        Config.debug(f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        return

    # get reporter & reported
    reporter = SQL.get_player(detection['reporter'])
    reported = SQL.get_player(detection['reported'])

    create = 0
    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = SQL.insert_player(detection['reporter'])
        create += 1

    if reported is None:
        reported = SQL.insert_player(detection['reported'])
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
            Config.debug(f'      Completed {idx}/{len(detections)}')

    Config.debug(f'      Done: Completed {idx} detections')


@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(manual_detect=0):
    detections = request.get_json()
    manual_detect = 0 if int(manual_detect) == 0 else 1
    # remove duplicates
    df = pd.DataFrame(detections)
    df.drop_duplicates(subset=['reporter','reported','region_id'], inplace=True)

    if len(df) > 5000 or df["reporter"].nunique() > 1:
        print('to many reports')
        Config.debug('to many reports')
        return jsonify({'NOK': 'NOK'}), 400
    
    detections = df.to_dict('records')

    print(f'      Received detections: DF shape: {df.shape}')
    Config.debug(msg=f'      Received detections: DF shape: {df.shape}')
    Config.sched.add_job(insync_detect ,args=[detections, manual_detect], replace_existing=False, name='detect')

    return jsonify({'OK': 'OK'})


@detect.route('/plugin/detect/<rsn>', methods=['GET'])
def get_detects(rsn=""):
    result = SQL.get_times_manually_reported(rsn)

    try:
        times_reported = int(result[0][0])
    except TypeError:
        times_reported = 0

    return jsonify({'times_reported': times_reported})
