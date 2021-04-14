import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, make_response
import json
import numpy as np

import Config
from Predictions import model
from SQL import get_player, insert_prediction_feedback, get_verified_discord_user

app_predictions = Blueprint('predictions', __name__, template_folder='templates')

@app_predictions.route('/site/prediction/<player_name>', methods=['POST', 'GET'])
def get_prediction(player_name):
    df = model.predict_model(player_name=player_name)
    df['name'] = player_name

    if isinstance(df, dict):
        return jsonify(df)

    prediction_dict = df.to_dict(orient='records')[0]

    print(prediction_dict)

    return_dict = {
        "player_id": int(prediction_dict.pop("id")),
        "player_name": prediction_dict.pop("name"),
        "prediction_label": prediction_dict.pop("prediction"),
        "prediction_confidence": prediction_dict.pop("Predicted confidence"),
        "secondary_predictions": sort_predictions(prediction_dict)
    }


    return jsonify(return_dict)

@app_predictions.route('/plugin/predictionfeedback/', methods=['POST', 'OPTIONS'])
def receive_plugin_feedback():

    #Preflight
    if request.method == 'OPTIONS':
        response = make_response()
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response

    vote_info = request.get_json()

    player_id_db = get_player(vote_info["rsn"])

    if int(player_id_db.id) == int(vote_info["voter_id"]):
        insert_prediction_feedback(vote_info)

    return 'OK'


@app_predictions.route('/discord/predictionfeedback/', methods=['POST', 'OPTIONS'])
def receive_discord_feedback():
    # Preflight
    if request.method == 'OPTIONS':
        response = make_response()
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response

    vote_info = request.get_json()

    discord_link = get_verified_discord_user(vote_info["discord_id"])

    if(discord_link):
        print(discord_link)

        if int(discord_link[0].Discord_id) == int(vote_info["discord_id"]):
            vote_info["voter_id"] = discord_link[0].Player_id
            vote_info["subject_id"] = get_player(vote_info["name"])
            insert_prediction_feedback(vote_info)
        else:
            return "<h1>400</h1><p>You are not permitted to vote from this account.</p>", 400

    else:
        return "<h1>400</h1><p>Use the !link command to link a Runescape account to your discord account first.</p>", 400

    return 'OK'

def sort_predictions(preds):

    #removes any 0% prediction values then sorts the dictionary in descending order by value
    return list(sorted(({k: v for k, v in preds.items() if v > 0}).items(),  key=lambda item: item[1], reverse=True))


