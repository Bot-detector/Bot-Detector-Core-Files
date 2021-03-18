from flask import Blueprint, request
import SQL
from flask.json import jsonify

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')


@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(contributor=""):

    if(contributor==""):
        return "<h1>404</h1><p>You must include a Runescape Name in your query.</p>", 400
    else:
        contributions = SQL.get_contributions(contributor)

        return contributions


