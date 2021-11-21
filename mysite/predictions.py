import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Config
import pandas as pd
import SQL
from discord_webhook import DiscordWebhook
from discord_webhook.webhook import DiscordEmbed
from flask import Blueprint, jsonify, make_response, request
from SQL import (get_player, get_verified_discord_user,
                 insert_prediction_feedback)
from utils.string_processing import escape_markdown, to_jagex_name, is_valid_rsn


app_predictions = Blueprint('predictions', __name__, template_folder='templates')


def get_prediction_from_db(player):
    try:
        player = SQL.get_normalized_player(player)
        df_resf = SQL.get_prediction_player(player.id)
        df_resf = pd.DataFrame(df_resf)
        df_resf.set_index('name', inplace=True)
        df_resf.rename(columns={'Predicted_confidence': 'Predicted confidence'}, inplace=True)

        columns = [c for c in df_resf.columns.tolist() if not(c in ['id','prediction', 'created'])]
        df_resf.loc[:, columns]= df_resf[columns].astype(float)/100

        return df_resf
    except Exception as e:
        Config.debug(f'error in get_prediction_from_db: {e}')
        return None

@app_predictions.route('/site/prediction/<player_name>', methods=['POST', 'GET'])
@app_predictions.route('/<version>/site/prediction/<player_name>', methods=['POST', 'GET'])
def get_prediction(player_name, version=None):
    if is_valid_rsn(player_name):
        normalized_name = to_jagex_name(player_name)
        df = get_prediction_from_db(normalized_name)

        if df is None:
            df = {
                "player_id": -1,
                "player_name": player_name,
                "prediction_label": "Prediction not in database",
                "prediction_confidence": 0
            }
            return jsonify(df)

        df['name'] = player_name

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

    else:
        df = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Invalid player name",
            "prediction_confidence": 0
        }
        return jsonify(df)
   
# delete this beast later
def sort_predictions(d):
    # remove 0's
    d = {key: value for key, value in d.items() if value > 0}
    # sort dict decending
    d = list(sorted(d.items(), key=lambda x: x[1], reverse=True))
    return d


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

    voter = get_player(vote_info['player_name'])

    if voter is None:
        voter = SQL.insert_player(vote_info['player_name'])

    # Voter ID will be 0 if player is not logged in.
    # There is a plugin check for this also.
    if(int(voter.id) > 0):
        vote_info["voter_id"] = voter.id

        insert_prediction_feedback(vote_info)

        if vote_info["feedback_text"] != None:
            broadcast_feedback(vote_info)

    else:
        Config.debug(f'prediction feedback error: {vote_info}')

    return jsonify({'OK':'OK'})


def broadcast_feedback(feedback):

    if feedback["vote"] == 1:
        embed_color="009302"
        vote_name="Looks good!"
    elif feedback["vote"] == 0:
        embed_color="6A6A6A"
        vote_name="Not sure.."
    else:
        embed_color="FF0000"
        vote_name="Looks wrong."

    subject = SQL.get_player_names([feedback["subject_id"]])[0]

    webhook = DiscordWebhook(url=Config.feedback_webhook_url)

    embed = DiscordEmbed(title="New Feedback Submission", color=embed_color)

    embed.add_embed_field(name="Voter Name", value=f"{feedback['player_name']}", inline=False)
    embed.add_embed_field(name="Subject Name", value=f"{subject.name} ", inline=False)
    embed.add_embed_field(name="Prediction", value=f"{feedback['prediction'].replace('_', ' ')}")
    embed.add_embed_field(name="Confidence", value=f"{feedback['confidence'] * 100:.2f}%")
    embed.add_embed_field(name="Vote", value=f"{vote_name}", inline=False)
    embed.add_embed_field(name="Explanation", value=f"{escape_markdown(feedback['feedback_text'])}", inline=False)

    if feedback["vote"] == -1 and feedback.get('proposed_label'):
        embed.add_embed_field(name="Proposed Label", value=f"{feedback['proposed_label'].replace('_', ' ')}")

    embed.set_footer(text=datetime.datetime.utcnow().strftime('%a %B %d %Y  %I:%M:%S %p'))

    webhook.add_embed(embed=embed)
    webhook.execute()

    return
