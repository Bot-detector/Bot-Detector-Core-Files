from flask import Blueprint, request
from flask.json import jsonify
from Functions.SQL import insert_report
import concurrent.futures as cf

detect = Blueprint('detect', __name__, template_folder='templates')

def multi_thread(tasks):
    with cf.ProcessPoolExecutor() as executor:
        futures = {executor.submit(insert_report, task[0]) for task in tasks}
        for future in cf.as_completed(futures):
            _ = future.result()

@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
def post_detect(manual_detect=0):
    detections = request.get_json()
    tasks = []

    for detection in detections:
        detection['manual_detect'] = 0 if int(manual_detect) == 0 else 1
        print(f'Detected: {detection}')
        
        tasks.append(([detection]))
        
    multi_thread(tasks)
    return jsonify({'OK': 'OK'})
