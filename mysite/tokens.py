import os, sys

from sqlalchemy.sql.expression import false
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from flask import Blueprint, request, make_response, after_this_request, render_template_string, redirect
from flask.json import jsonify

import pandas as pd
import json

import SQL
import Config
from Predictions import model
from scraper import banned_by_jagex, hiscoreScraper

app_token = Blueprint('app_token', __name__, template_folder='templates')

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


'''
    Tokens with extra verification on token
'''
def verify_token(token, verifcation):
    player_token = SQL.get_token(token)

    if not (player_token):
        return False

    if verifcation == "hiscores":
        if not (player_token.request_highscores == 1):
            return False

    if verifcation == "ban":
        if not (player_token.verify_ban == 1):
            return False

    if verifcation == "create_token":
        if not (player_token.create_token == 1):
            return False

    if verifcation == "verify_players":
        if not (player_token.verify_players == 1):
            return False

    return True

@app_token.route("/log/<token>", methods=['GET'])
def print_log(token):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    with open("error.log", "r") as f:
        content = f.read()
        return render_template_string("<pre>{{ content }}</pre>", content=content)


@app_token.route('/site/highscores/<token>', methods=['POST', 'GET'])
@app_token.route('/site/highscores/<token>/<ofInterest>', methods=['POST', 'GET'])
def get_highscores(token, ofInterest=None):

    if not (verify_token(token, verifcation='hiscore')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    if ofInterest is None:
        data = SQL.get_highscores_data()
    else:
        data = SQL.get_hiscores_of_interst()

    # format data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))


@app_token.route('/site/verify/<token>', methods=['POST', 'OPTIONS'])
def verify_bot(token):

    #Preflight
    if request.method == 'OPTIONS':
        response = make_response()
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response

    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    form_data = request.get_json()

    # input verification
    bot, bot_int = intTryParse(form_data['bot'])
    label, label_int = intTryParse(form_data['label'])

    playerNames = form_data['names']

    if not (bot_int) or len(playerNames) == 0:
        return "Invalid Parameters", 405

    # get data
    for name in playerNames:

        player = SQL.get_player(name)

        if player:
            if bot == 0:
                SQL.update_player(player.id, possible_ban=0,
                          confirmed_ban=0, label_id=1, confirmed_player=1)
            else:
                SQL.update_player(player.id, possible_ban=1,
                          confirmed_ban=1, label_id=label, confirmed_player=0)

    return 'OK'


@app_token.route('/site/token/<token>/<player_name>/<hiscore>')
@app_token.route('/site/token/<token>/<player_name>/<hiscore>/<ban>')
def create_user_token(token, player_name, hiscore=0, ban=0):

    if not (verify_token(token, verifcation='create_token')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # Create token
    token = SQL.create_token(player_name, highscores=hiscore, verify_ban=ban)

    # return created token
    return jsonify({'Token': token})


'''
    These routes schedule jos
'''
@app_token.route("/site/possible_ban/<token>")
def possible_ban(token):
    if not (verify_token(token, verifcation='create_token')):
        return "<h1>404</h1><p>Invalid token</p>", 404
        
    Config.sched.add_job(banned_by_jagex.confirm_possible_ban, max_instances=10, coalesce=True, name='confirm_possible_ban')
    return jsonify({'OK': 'OK'})

@app_token.route('/site/save_model/<token>')
def create_predictions(token):
    if not (verify_token(token, verifcation='create_token')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    Config.sched.add_job(model.save_model ,args=[Config.n_pca, Config.use_pca], replace_existing=True, name='save_model')
    return jsonify({'OK': 'OK'})

@app_token.route("/site/hiscorescraper/<token>")
def hiscorescraper(token):
    if not (verify_token(token, verifcation='create_token')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    Config.sched.add_job(hiscoreScraper.run_scraper, name='run_hiscore',max_instances=10, coalesce=True)
    return jsonify({'OK': 'OK'})
'''
    These routes are accessible if you have a token
'''

@app_token.route('/site/player/<token>/<player_name>', methods=['GET', 'POST'])
def get_player_route(token, player_name):
    # verify token
    if not (verify_token(token, verifcation=None)):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    data = SQL.get_player(player_name)

    # if there is no data return
    if data is None:
        return "<h1>404</h1><p>Player not found</p>", 404

    # parse data
    df = pd.DataFrame([data])
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))

@app_token.route('/site/players/<token>', methods=['GET', 'POST'])
@app_token.route('/site/players/<token>/<ofInterest>', methods=['GET', 'POST'])
def get_players(token, ofInterest=None):
    # verify token
    if not (verify_token(token, verifcation=None)):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    if ofInterest is None:
        data = SQL.get_player_names()
    else:
        data = SQL.get_players_of_interest()

    # parse data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))


@app_token.route('/site/labels/<token>', methods=['GET', 'POST'])
def get_labels(token):
    # verify token
    if not (verify_token(token, verifcation=None)):
        return "<h1>404</h1><p>Invalid token</p>", 404

    # get data
    data = SQL.get_player_labels()

    # parse data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))


@app_token.route('/site/discord_user/<token>', methods=['POST', 'OPTIONS'])
@app_token.route('/<version>/site/discord_user/<token>', methods=['POST', 'OPTIONS'])
def verify_discord_user(token, version=None):
    #Preflight
    if request.method == 'OPTIONS':
        response = make_response()
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response

    if not (verify_token(token, verifcation='verify_players')):
        return jsonify({"error": "Invalid token."}), 401

    verify_data = request.get_json()

    player = SQL.get_player(verify_data["player_name"])

    if(player is None):
        return jsonify({"error": "Could not find player."}), 400

    discord_links = SQL.get_discord_user_link(player.id)

    token_id = SQL.get_token(token).id

    matched_code_found = False
    already_linked = False

    if(discord_links):
        for record in discord_links:
            if str(record.Code) == str(verify_data["code"]):
                SQL.set_discord_verification(id=record.Entry, token=token_id)
                matched_code_found = True

                if int(record.Verified_status) == 1:
                    already_linked = True

                break

    else:
        if matched_code_found:
            if already_linked:
                return jsonify({"error": "User has already been verified."}), 400
            else:
                return jsonify({"success": "User was successfully verified."}), 200
        else:
            if(discord_links):
                return jsonify({"error": f"Code submitted by {player.name} was incorrect."}), 400
            else:
                return jsonify({"error": f"{player.name} has no pending Discord links."}), 400


# CORS Policy: Allow Access to These Methods From Any Origin
@app_token.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         "Origin, X-Requested-With, Content-Type, Accept, x-auth")
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, OPTIONS, PUT, PATCH, DELETE')
    return response

