import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify
import json

import Config
from Predictions import model

app_predictions = Blueprint('predictions', __name__, template_folder='templates')

@app_predictions.route('/site/prediction/<player_name>', methods=['POST', 'GET'])
def get_prediction(player_name):
    df = model.predict_model(player_name=player_name)
    df['name'] = player_name
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))