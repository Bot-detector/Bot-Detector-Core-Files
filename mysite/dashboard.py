from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_number_confirmed_bans, get_number_tracked_players, get_report_stats

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

#######################
# Dashboard Endpoints #
#######################


@dashboard.route('/site/dashboard/gettotaltrackedplayers', methods=['GET'])
def get_total_tracked_players():
    num_of_players = get_number_tracked_players()
    return_dict = {
        "players": num_of_players[0]
    }

    return jsonify(return_dict)


@dashboard.route('/site/dashboard/getreportsstats', methods=['GET'])
def get_total_reports():
    report_stats = get_report_stats()[0]

    return_dict = {
        "bans": int(report_stats[0]),
        "false_reports": int(report_stats[1]),
        "total_reports": int(report_stats[2]),
        "accuracy": float(report_stats[3])
    }

    return return_dict


# CORS Policy: Allow Access to These Methods From Any Origin
@dashboard.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response
