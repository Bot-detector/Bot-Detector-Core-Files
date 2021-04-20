import SQL
from flask.json import jsonify
from flask import Blueprint, request
import mysite.tokens as tokens
import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


discord = Blueprint('discord', __name__, template_folder='templates')


@discord.route('/discord/locations/<token>', methods=['GET', 'POST'])
def get_locations(token):

    verified = tokens.verify_token(token=token, verifcation='create_token')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    # json = {'names':('ferrariic','extreme4all','seltzerbro')}
    players = request.get_json()

    if players is None:
        return jsonify({'Invalid Data':'Data'})

    players = players['names']
    data = SQL.get_player_report_locations(players)
    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

    # some code