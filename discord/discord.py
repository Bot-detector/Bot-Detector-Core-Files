import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import SQL
from flask.json import jsonify
from flask import Blueprint, request
import mysite.tokens as tokens
import Config
import pandas as pd


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
  

@discord.route('/discord/verify/player_rsn_discord_account_status/<token>/<player_name>', methods=['GET', 'POST'])
def get_verification_status_information(token, player_name=None):

    verified = tokens.verify_token(token=token, verifcation='verify_players')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    if player_name is None:
        return jsonify({'Invalid Name':'Invalid Name'})
    
    data = SQL.get_verification_info(player_name)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/verify/playerid/<token>/<player_name>', methods=['GET', 'POST'])
def get_verification_playerid_information(token, player_name=None):

    verified = tokens.verify_token(token=token, verifcation='verify_players')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    if player_name is None:
        return jsonify({'Invalid Name':'Invalid Name'})
    
    data = SQL.get_verification_player_id(player_name)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/verify/verified_player_info/<token>/<player_name>', methods=['GET', 'POST'])
def get_verified_player_list_information(token, player_name=None):

    verified = tokens.verify_token(token=token, verifcation='verify_players')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    if player_name is None:
        return jsonify({'Invalid Name':'Invalid Name'})
    
    data = SQL.get_verified_info(player_name)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

@discord.route('/discord/verify/insert_player_dpc/<token>/<discord_id>/<player_id>/<code>', methods=['GET', 'POST'])
def post_verified_insert_information(token, discord_id=None, player_id=None, code=None):

    verified = tokens.verify_token(token=token, verifcation='verify_players')

    if not (verified):
        return jsonify({'Invalid Data':'Data'})

    if discord_id is None:
        return jsonify({'Invalid Discord':'Invalid Discord ID'})

    if player_id is None:
        return jsonify({'Invalid Player ID':'Invalid Player ID'})

    if code is None:
        return jsonify({'Invalid Code':'Invalid Code'})
    
    data = SQL.verificationInsert(discord_id, player_id, code)

    return jsonify({'Value':f'{discord_id} {player_id} {code} Submitted'})
