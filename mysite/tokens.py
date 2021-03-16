from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_token, get_player, update_player, get_highscores_data, get_player_names
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


@app_token.route('/site/verify/<token>/<playername>/<bot>', methods=['GET', 'POST'])
def verify_bot(token, playername, bot):
    player_token = get_token(token)

    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].verify_ban == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404
    
    bot = 0 if int(bot) == 0 else 1
    player = get_player(playername)
    
    if bot == 0:
        update_player(player.id, possible_ban=0, confirmed_ban=0, confirmed_player=1)
    else:
        update_player(player.id, possible_ban=1, confirmed_ban=1, confirmed_player=0)
    return jsonify({'OK': 'report verified'})

@app_token.route('/site/players/<token>', methods=['GET', 'POST'])
def get_players(token):
    player_token = get_token(token)
    print(player_token)
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = get_player_names()
    df = pd.DataFrame(data)
    return jsonify(json.loads(df.to_json(orient='records')))