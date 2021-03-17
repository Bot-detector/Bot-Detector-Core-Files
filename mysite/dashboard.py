from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_number_confirmed_bans, get_number_tracked_players, get_report_stats
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
        "players": num_of_players[0]
    }

    return jsonify(return_dict)

@dashboard.route('/site/dashboard/getreportsstats', methods=['GET'])
def get_total_reports():
    report_stats = get_report_stats()
    print(report_stats)
    print(type(report_stats))
    return jsonify(report_stats)

# CORS Policy: Allow Access to These Methods From Any Origin
@dashboard.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response