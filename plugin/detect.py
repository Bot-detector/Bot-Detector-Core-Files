from flask import Blueprint, request
from flask.json import jsonify
import SQL, Config
import concurrent.futures as cf
import pandas as pd

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
    print(detection)
    

def multi_thread(tasks):
    with cf.ProcessPoolExecutor() as executor:
        futures = {executor.submit(custom_hiscore, task[0]) for task in tasks}
        for future in cf.as_completed(futures):
            _ = future.result()


@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(manual_detect=0):
    detections = request.get_json()
    manual_detect = 0 if int(manual_detect) == 0 else 1
    tasks = []
    
    # multithread might cause issue on server
    mt = True
    job = True

    # remove duplicates
    df = pd.DataFrame(detections)
    df.drop_duplicates(subset=['reporter','reported','region_id'],inplace=True)
    detections = df.to_dict('records')

    for detection in detections:
        detection['manual_detect'] = manual_detect
        # print(f'Detected: {detection}')
        if mt:
            tasks.append(([detection]))
        else:
            # note when using lambda you cannot have return values
            if job:
                Config.sched.add_job(lambda: custom_hiscore(detection))
            else:
                custom_hiscore(detection)
    if mt:
        # note when using lambda you cannot have return values
        if job:
            Config.sched.add_job(lambda: multi_thread(tasks))
        else:
            multi_thread(tasks)

        

    return jsonify({'OK': 'OK'})
