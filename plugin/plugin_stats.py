from flask import Blueprint, request
import SQL
from flask.json import jsonify

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')


@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(contributor=""):
    contributions = SQL.get_contributions(contributor)

    return_dict = {
        "num_reported": 0,
        "players_banned": 0
    }

    return "OK"


