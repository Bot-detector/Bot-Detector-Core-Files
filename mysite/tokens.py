from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_token, get_player, update_player, get_highscores_data, get_player_names, get_player_labels
import pandas as pd
import json
app_token = Blueprint('app_token', __name__, template_folder='templates')


def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


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


@app_token.route('/site/verify/<token>/<playername>')
@app_token.route('/site/verify/<token>/<playername>/<bot>/')
@app_token.route('/site/verify/<token>/<playername>/<bot>/<label>')
def verify_bot(token, playername, bot=0, label=0):
    # token verification
    player_token = get_token(token)

    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].verify_ban == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    player = get_player(playername)

    # input verification
    bot, bot_int = intTryParse(bot)
    label, label_int = intTryParse(label)

    if not (label_int) or not (bot_int) or player == None:
        return "<h1>404</h1><p>Invalid parameters</p>", 404

    if bot == 0:
        update_player(player.id, possible_ban=0, confirmed_ban=0,
                      label_id=player.label_id, confirmed_player=1)
    else:
        update_player(player.id, possible_ban=1,
                      confirmed_ban=1, label_id=label, confirmed_player=0)

    return jsonify({'OK': 'report verified', 'bot': bot})


@app_token.route('/site/players/<token>', methods=['GET', 'POST'])
def get_players(token):
    player_token = get_token(token)
    print(player_token)
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = get_player_names()
    df = pd.DataFrame(data)
    return jsonify(json.loads(df.to_json(orient='records')))


@app_token.route('/site/labels/<token>', methods=['GET', 'POST'])
def get_labels(token):
    player_token = get_token(token)
    print(player_token)
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = get_player_labels()
    df = pd.DataFrame(data)
    return jsonify(json.loads(df.to_json(orient='records')))
