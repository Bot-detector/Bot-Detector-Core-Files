from flask import Blueprint, request
import SQL

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')

@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
@plugin_stats.route('/<version>/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(version=None, contributor=""):

    if(contributor==""):
        return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    else:
        contributions = SQL.get_contributions(contributor)

        possible_bans = 0
        confirmed_bans = 0

        for c in contributions:
            possible_bans += c[3]
            confirmed_bans += c[2]

        return_dict = {
            "reports": len(contributions),
            "bans": confirmed_bans,
            "possible_bans": possible_bans
        }

        return return_dict

@plugin_stats.route('/stats/getcontributorid/<contributor>', methods=['GET'])
def get_contributor_id(contributor=""):
    if (contributor == ""):
        return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    else:
        player = SQL.get_player(contributor)

        if(player):
            return_dict = {
                "id": player.id
            }

            return return_dict
        else:
            return "<h1>400</h1><p>Player not found.</p>", 400

