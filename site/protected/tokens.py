from flask import Blueprint, request
from flask.json import jsonify
from Functions.SQL import get_token, get_player, update_player, get_highscores_data
import pandas as pd
import json
app_token = Blueprint('app_token', __name__, template_folder='templates')


@app_token.route('/site/highscores/<token>', methods=['GET', 'POST'])
def get_highscores(token):
    player_token = get_token(token)
    print(player_token)
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].request_highscores == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = get_highscores_data()
    df = pd.DataFrame(data)
    return jsonify(json.loads(df.to_json(orient='records')))


@app_token.route('/site/verify/<token>/<playername>', methods=['GET', 'POST'])
def verify_bot(token, playername):
    player_token = get_token(token)

    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].verify_ban == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    player = get_player(playername)
    print(player)
    update_player(player.id, possible_ban=1, confirmed_ban=1)
    return jsonify({'OK': 'report verified'})