# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request
from flask.json import jsonify
import pandas as pd
from flask_restplus import Api, Resource
# custom imports
import Config
from SQL import composite
import plugin.functions as functions


detect = Blueprint('detect', __name__)
api = Api(detect)


@detect.route('/plugin/detect/<manual_detect>', methods=['POST'])
class Detect(Resource):
    def post(manual_detect=0):
        detections = request.get_json()
        manual_detect = 0 if int(manual_detect) == 0 else 1

        # remove duplicates
        df = pd.DataFrame(detections)
        df.drop_duplicates(subset=['reporter','reported','region_id'], inplace=True)

        Config.debug(f'      Received detections: DF shape: {df.shape}')
        
        detections = df.to_dict('records')
        del df # memory optimalisation
        
        Config.sched.add_job(functions.insync_detect ,args=[detections, manual_detect], replace_existing=False, name='detect')

        return jsonify({'OK': 'OK'})