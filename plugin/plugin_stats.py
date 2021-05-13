from flask import Blueprint, request
import SQL

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')

@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
@plugin_stats.route('/<version>/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(version=None, contributor=""):

    if(contributor==""):
        return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    else:
        try:
            passive_contributions = SQL.get_contributions(contributor, manual_report=0)
            manual_contributions = SQL.get_contributions(contributor, manual_report=1)
        except Exception as e:
            print(e)

        passive_reports = len(passive_contributions)
        passive_bans = 0
        passive_possible_bans = 0

        manual_reports = len(manual_contributions)
        manual_bans = 0
        manual_possible_bans = 0
        manual_real_player = 0

        for p in passive_contributions:
            passive_bans += p.confirmed_ban
            passive_possible_bans += p.possible_ban

        for m in manual_contributions:
            manual_bans += m.confirmed_ban
            manual_possible_bans += m.possible_ban

        passive_dict = {
            "reports": passive_reports,
            "bans": passive_bans,
            "possible_bans": passive_possible_bans
        }

        manual_dict = {
            "reports": manual_reports,
            "bans": manual_bans,
            "possible_bans": manual_possible_bans,
            "incorrect_reports": manual_real_player,
        }

        total_dict = {
            "reports": passive_reports + manual_reports,
            "bans": passive_bans + manual_bans,
            "possible_bans": passive_possible_bans + manual_possible_bans
        }

        return_dict = {
            "passive": passive_dict,
            "manual": manual_dict,
            "total": total_dict
        }
        
        if version in ['1.3','1.3.1'] or None:
            return total_dict

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

