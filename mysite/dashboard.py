from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_number_confirmed_bans, get_number_tracked_players
import json

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

#######################
# Dashboard Endpoints #
#######################

@dashboard.route('/site/dashboard/gettotalbans', methods=['GET'])
def get_total_bans():
    num_of_bans = get_number_confirmed_bans()
    return_dict = {
        "bans": num_of_bans
    }

    return jsonify(return_dict)

@dashboard.route('/site/dashboard/gettotaltrackedplayers', methods=['GET'])
def get_total_tracked_players():
    num_of_players = get_number_tracked_players()
    return_dict = {
        "players": num_of_players
    }

    return jsonify(return_dict)

# CORS Policy: Allow Access to These Methods From Any Origin
@dashboard.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response