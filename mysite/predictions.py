import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, make_response
import json
import numpy as np

import Config
from Predictions import model
from SQL import get_player, insert_prediction_feedback, get_verified_discord_user
import SQL


app_predictions = Blueprint('predictions', __name__, template_folder='templates')

@app_predictions.route('/site/prediction/<player_name>', methods=['POST', 'GET'])
@app_predictions.route('/<version>/site/prediction/<player_name>', methods=['POST', 'GET'])
@app_predictions.route('/<version>/site/prediction/<player_name>/<debug>', methods=['POST', 'GET'])
def get_prediction(player_name, version=None, debug=None):
    debug = True if debug is not None else False
    Config.debug(f'Precition route debug: {debug}')
    # Config.debug("PREDICTION REQUEST\n")
    # Config.debug(request.headers)

    player_name, bad_name = SQL.name_check(player_name)

    if player_name == "Mod Ash":
        df = {
            "player_id": 957580,
            "player_name": player_name,
            "prediction_label": "Big Daddy",
            "prediction_confidence": 1
        }
    elif not( bad_name):
        
        df = model.predict_model(player_name=player_name, use_pca=Config.use_pca, debug=debug)
        df['name'] = player_name
    else:
        df = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Invalid player name",
            "prediction_confidence": 0
        }

    if isinstance(df, dict):
        return jsonify(df)

    
    prediction_dict = df.to_dict(orient='records')[0]
    prediction_dict['id'] = int(prediction_dict['id'])
    prediction_dict.pop("created")

    return_dict = {
        "player_id":                prediction_dict.pop("id"),
        "player_name":              prediction_dict.pop("name"),
        "prediction_label":         prediction_dict.pop("prediction"),
        "prediction_confidence":    prediction_dict.pop("Predicted confidence"),
        #"predictions_breakdown":    prediction_dict
    }
    if version is None:
        return_dict['secondary_predictions'] = sort_predictions(prediction_dict)
    else:
        return_dict['predictions_breakdown'] = prediction_dict

    return jsonify(return_dict)

@app_predictions.route('/plugin/predictionfeedback/', methods=['POST', 'OPTIONS'])
@app_predictions.route('/<version>/plugin/predictionfeedback/', methods=['POST', 'OPTIONS'])
def receive_plugin_feedback(version=None):

    #Preflight
    if request.method == 'OPTIONS':
        response = make_response()
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response

    vote_info = request.get_json()

    print(vote_info)

    voter = get_player(vote_info['player_name'])

    # Voter ID will be 0 if player is not logged in.
    # There is a plugin check for this also.
    if(int(voter.id) > 0):
        vote_info["voter_id"] = voter.id

        insert_prediction_feedback(vote_info)
    else:
        Config.debug(f'prediction feedback error: {vote_info}')

    return jsonify({'OK':'OK'})


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

            vote_info["subject_id"] = get_player(vote_info["name"]).id

            insert_prediction_feedback(vote_info)
        else:
            return "<h1>400</h1><p>You are not permitted to vote from this account.</p>", 400

    else:
        return "<h1>400</h1><p>Use the !link command to link a Runescape account to your discord account first.</p>", 400

    return 'OK'

# delete this beast later
def sort_predictions(d):
    # remove 0's
    d = {key: value for key, value in d.items() if value > 0}
    # sort dict decending
    d = list(sorted(d.items(), key=lambda x: x[1], reverse=True))
    return d