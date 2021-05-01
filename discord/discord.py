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

    verified = tokens.verify_token(token=token, verifcation='hiscores')

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

@discord.route('/discord/region/<token>', methods=['GET', 'POST'])
@discord.route('/discord/region/<token>/<regionName>', methods=['GET', 'POST'])
def get_regions(token, regionName=None):

    verified = tokens.verify_token(token=token, verifcation='hiscores')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})
        
    if regionName is None:
        regionName = request.get_json()

        if regionName is None:
            return jsonify({'Invalid Data':'Data'})

        regionName = regionName['region']
    
    data = SQL.get_region_search(regionName)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/heatmap/<token>', methods=['GET', 'POST'])
@discord.route('/discord/heatmap/<token>/<region_id>', methods=['GET', 'POST'])
def get_heatmap_data(token, region_id=None):

    verified = tokens.verify_token(token=token, verifcation='hiscores')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})
    print(region_id)
    if region_id is None:
        region_id = request.get_json()

        if region_id is None:
            return jsonify({'Invalid Data':'Data'})

        region_id = region_id['region_id']
    
    data = SQL.get_report_data_heatmap(region_id)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/player_bans/<token>', methods=['GET', 'POST'])
@discord.route('/discord/player_bans/<token>/<player_name>', methods=['GET', 'POST'])
def get_player_bans(token, player_name=None):

    verified = tokens.verify_token(token=token, verifcation='hiscores')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    if player_name is None:
        player_name = request.get_json()
    
        if player_name is None:
            return jsonify({'Invalid Data':'Data'})

        player_name = player_name['player_name']
    
    data = SQL.get_player_banned_bots(player_name)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/player_verification_status/<token>/<player_name>', methods=['GET', 'POST'])
def get_player_verification(token, player_name=None):

    verified = tokens.verify_token(token=token, verifcation='create_token')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    player_name = request.get_json()

    if player_name is None:
        return jsonify({'Invalid Data':'Data'})

    player_name = player_name['player_name']
    
    data = SQL.get_discord_verification_status(player_name)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)
  
@discord.route('/discord/locations/<token>/<player_name>', methods=['GET'])
def get_location():
    pass