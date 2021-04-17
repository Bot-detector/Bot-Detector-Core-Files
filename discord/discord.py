from flask import Blueprint, request
from flask.json import jsonify
import SQL
import json
import pandas as pd


discord = Blueprint('discord', __name__, template_folder='templates')

# moved to token
@discord.route('/discord/player_location/<player_name>', methods=['GET'])
def get_player_location(player_name):
    return
    data = SQL.get_player_location(player_name)
    # parse data
    df = pd.DataFrame(data)
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))