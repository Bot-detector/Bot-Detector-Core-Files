from flask import Blueprint, request
from flask.json import jsonify
from SQL import get_number_confirmed_bans
import json

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

#######################
# Dashboard Endpoints #
#######################

@dashboard.route('/site/dashboard/gettotalbans', methods=['GET'])
def get_total_bans():
    num_of_bands = get_number_confirmed_bans()
    return_str = '{"bans": " + str(num_of_bands) + "}'

    return jsonify(return_str)
