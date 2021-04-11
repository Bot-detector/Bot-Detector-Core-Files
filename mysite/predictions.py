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

    mask = (df['Predicted confidence'] < 0.75)
    df.loc[mask, 'prediction'] = 'Unsure'

    prediction_dict = df.to_dict(orient='records')[0]

    return_dict = {
        "player_id": int(prediction_dict.pop("id")),
        "player_name": prediction_dict.pop("name"),
        "prediction_label": prediction_dict.pop("prediction"),
        "prediction_confidence": prediction_dict.pop("Predicted confidence"),
        "secondary_predictiions": sort_predictions(prediction_dict)
    }


    return json.dumps(return_dict, sort_keys=False)

def sort_predictions(preds):

    #removes any 0% prediction values then sorts the dictionary in descending order by value
    return list(sorted(({k: v for k, v in preds.items() if v > 0}).items(),  key=lambda item: item[1], reverse=True))


