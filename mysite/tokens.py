from flask import Blueprint, request
from flask.json import jsonify
import SQL
import pandas as pd
import json

app_token = Blueprint('app_token', __name__, template_folder='templates')


def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


'''
    Tokens with extra verification on token
'''


@app_token.route('/site/highscores/<token>', methods=['GET', 'POST'])
def get_highscores(token):
    # get token
    player_token = SQL.get_token(token)

    # verify token
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].request_highscores == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    data = SQL.get_highscores_data()

    # format data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))


@app_token.route('/site/verify/<token>/<playername>')
@app_token.route('/site/verify/<token>/<playername>/<bot>')
@app_token.route('/site/verify/<token>/<playername>/<bot>/<label>')
def verify_bot(token, playername, bot=0, label=0):
    # get token
    player_token = SQL.get_token(token)

    # verify token
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].verify_ban == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    player = SQL.get_player(playername)

    # input verification
    bot, bot_int = intTryParse(bot)
    label, label_int = intTryParse(label)

    if not (label_int) or not (bot_int) or player == None:
        return "<h1>404</h1><p>Invalid parameters</p>", 404

    # player is a bot
    if bot == 0:
        SQL.update_player(player.id, possible_ban=0,
                          confirmed_ban=0, label_id=1, confirmed_player=1)
    else:
        SQL.update_player(player.id, possible_ban=1,
                          confirmed_ban=1, label_id=label, confirmed_player=0)

    return jsonify({'OK': 'report verified', 'bot': bot})


@app_token.route('/site/token/<token>/<player_name>/<hiscore>')
@app_token.route('/site/token/<token>/<player_name>/<hiscore>/<ban>')
def create_user_token(token, player_name, hiscore=0, ban=0):
    # get token
    player_token = SQL.get_token(token)

    # verify token
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    if not (player_token[0].create_token == 1):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # Create token
    token = SQL.create_token(player_name, highscores=hiscore, verify_ban=ban)

    # return created token
    return jsonify({'Token': token})


'''
    These routes are accessible if you have a token
'''


@app_token.route('/site/players/<token>', methods=['GET', 'POST'])
def get_players(token):
    # get token
    player_token = SQL.get_token(token)

    # verify token
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    data = SQL.get_player_names()

    # parse data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))


@app_token.route('/site/labels/<token>', methods=['GET', 'POST'])
def get_labels(token):
    # get token
    player_token = SQL.get_token(token)

    # verify token
    if not (player_token):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    data = SQL.get_player_labels()

    # parse data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))
