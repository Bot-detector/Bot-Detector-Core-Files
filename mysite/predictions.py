import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify
import json
import numpy as np

import Config
from Predictions import model

app_predictions = Blueprint('predictions', __name__, template_folder='templates')

@app_predictions.route('/site/prediction/<player_name>', methods=['POST', 'GET'])
def get_prediction(player_name):
    df = model.predict_model(player_name=player_name)
    df['name'] = player_name
    print(df.head())

    mask = (df['Predicted confidence'] < 0.75)
    df.loc[mask, 'prediction'] = 'Unsure'

    myjson = df.to_json(orient='records')

    return_dict = {
        "id": int(df['id']),
        "name": player_name,
        "prediction": df['prediction']
    }

    print(myjson)

    return jsonify(json.loads(myjson))
