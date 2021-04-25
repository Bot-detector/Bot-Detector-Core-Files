import SQL
from flask.json import jsonify
from flask import Blueprint, request
import mysite.tokens as tokens
import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


discord = Blueprint('discord', __name__, template_folder='templates')


@discord.route('/dev/discord/locations/<token>', methods=['GET', 'POST'])
def get_locations(token):
    print("Hello")

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

@discord.route('/dev/discord/region/<token>', methods=['GET', 'POST'])
def get_regions(token):

    verified = tokens.verify_token(token=token, verifcation='create_token')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    regionName = request.get_json()

    print(regionName)

    if regionName is None:
        return jsonify({'Invalid Data':'Data'})

    regionName = regionName['region']
    
    data = SQL.get_region_search(regionName)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/dev/discord/heatmap/<token>', methods=['GET', 'POST'])
def get_heatmap_data(token):

    verified = tokens.verify_token(token=token, verifcation='create_token')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    region_id = request.get_json()

    print(region_id)

    if region_id is None:
        return jsonify({'Invalid Data':'Data'})

    region_id = region_id['region_id']
    
    data = SQL.get_report_data_heatmap(region_id)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)