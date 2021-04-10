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
    prediction_data = model.predict_model(player_name=player_name)

    if prediction_data['player_id'] == -1:
        return json.dumps(prediction_data, sort_keys=False)
    else:

        top_prediction = prediction_data['proba_max'].to_dict(orient='records')[0]
        secondary_predictions = prediction_data['gnb_predictions'].to_dict(orient='records')[0]

        return_dict = {
            "player_id": prediction_data['player_id'],
            "player_name": prediction_data['player_name'],
            "prediction_label": prediction_data['prediction'],
            "prediction_confidence": top_prediction['Predicted confidence'],
            "secondary_predictions": sort_predictions(secondary_predictions)
        }

        if(return_dict['prediction_confidence'] < .75):
            return_dict['prediction_label'] = "Unsure"

        return json.dumps(return_dict, sort_keys=False)


def sort_predictions(preds):

    return list(sorted(preds.items(), key=lambda item: item[1]))

