from flask import Blueprint, request, make_response
import pandas as pd
from flask.json import jsonify
import SQL
import json

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')


@plugin_stats.route('/stats/contributions/', methods=['GET'])
@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
@plugin_stats.route('/<version>/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(version=None, contributor=None):

    if contributor is not None:
        contributors = [contributor]
    else:
        if isinstance(request.json, str):
            contrib_data = json.loads(request.json)
        else:
            contrib_data = request.json

        if contrib_data is not None:
            contributors = tuple([c["name"] for c in contrib_data ])
        else:
            return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    contributions = SQL.get_contributions(contributors)
    
    df = pd.DataFrame(contributions)
    df = df.drop_duplicates(inplace=False, subset=["reported_ids"], keep="last")

    try:
        df_detect_manual = df.loc[df['detect'] == 1]

        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_manual['possible_ban'].sum()),
            "incorrect_reports": int(df_detect_manual['confirmed_player'].sum())
        }
    except KeyError:
        manual_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0,
            "incorrect_reports": 0
        }

    try:
        df_detect_passive = df.loc[df['detect'] == 0]

        passive_dict = {
            "reports": len(df_detect_passive.index),
            "bans": int(df_detect_passive['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_passive['possible_ban'].sum())
        }
    except KeyError:
        passive_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0
        }

    total_dict = {
        "reports": passive_dict['reports'] + manual_dict['reports'],
        "bans": passive_dict['bans'] + manual_dict['bans'],
        "possible_bans": passive_dict['possible_bans'] + manual_dict['possible_bans']
    }

    if version in ['1.3','1.3.1'] or None:
        return jsonify(total_dict)

    return_dict = {
        "passive": passive_dict,
        "manual": manual_dict,
        "total": total_dict
    }

    return jsonify(return_dict)


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

