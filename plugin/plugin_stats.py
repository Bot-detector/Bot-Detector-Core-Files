from flask import Blueprint, request, make_response
import pandas as pd
from flask.json import jsonify
import SQL
import json
import utils.string_processing
import mysite.tokens as tokens
import Config

plugin_stats = Blueprint('plugin_stats', __name__, template_folder='templates')


@plugin_stats.route('/stats/contributions/', methods=['GET'])
@plugin_stats.route('/stats/contributions/<contributor>', methods=['GET'])
@plugin_stats.route('/<version>/stats/contributions/<contributor>', methods=['GET'])
def get_contributions(version=None, contributor=None):
    contributors = None

    # check if a signal contributor was given
    if not contributor == None:
        contributors = [contributor]
    
    # if contributors is not set we need to get the request data
    if contributors: # None == False
        data = request.json
        data = json.loads(data) if isinstance(data, str) else data
        contributors = tuple([c["name"] for c in data])

    # if for some reason contributors is still none
    if contributors is None:
        return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    contributions = SQL.get_contributions(contributors)

    df = pd.DataFrame(contributions)
    df = df.drop_duplicates(inplace=False, subset=["reported_ids", "detect"], keep="last")
    total_subs = len(df)

    try:
        df_detect_manual = df.loc[df['detect'] == 1]

        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_manual['possible_ban'].sum()),
            "incorrect_reports": int(df_detect_manual['confirmed_player'].sum())
        }

        manual_dict["possible_bans"] = manual_dict["possible_bans"] - manual_dict["bans"]

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
            "reports": total_subs - manual_dict["reports"],
            "bans": int(df_detect_passive['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_passive['possible_ban'].sum())
        }

        passive_dict["possible_bans"] = passive_dict["possible_bans"] - passive_dict["bans"]

    except KeyError:
        passive_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0
        }

    total_dict = {
        "reports": total_subs,
        "bans": passive_dict['bans'] + manual_dict['bans'],
        "possible_bans": passive_dict['possible_bans'] + manual_dict['possible_bans'],
        "feedback": len(pd.DataFrame(SQL.get_total_feedback_submissions(contributors)).index)
    }

    if version in ['1.3','1.3.1'] or None:
        return jsonify(total_dict)

    return_dict = {
        "passive": passive_dict,
        "manual": manual_dict,
        "total": total_dict
    }

    return jsonify(return_dict)


@plugin_stats.route('/stats/contributionsplus/<token>', methods=['GET'])
def get_contributions_plus(token):

    #TODO Figure out the name normalization situtation..
    if isinstance(request.json, str):
        contrib_data = json.loads(request.json)
    else:
        contrib_data = request.json

    if contrib_data is not None:
            contributors = tuple([c["name"] for c in contrib_data])
    else:
        return "<h1>400</h1><p>You must include a Runescape Name in your query.</p>", 400

    contributions = SQL.get_contributions(contributors)

    total_submissions_sql = '''
        SELECT
            COUNT(*) submissions
        FROM Reports as r
        JOIN Players as pl on pl.id = r.reportingID
        WHERE 1=1
        AND pl.name IN :contributors
    '''

    total_subs_data = SQL.execute_sql(sql=total_submissions_sql, param={"contributors": contributors})
    total_subs = int(total_subs_data[0].submissions)


    df = pd.DataFrame(contributions)
    df = df.drop_duplicates(inplace=False, subset=["reported_ids", "detect"], keep="last")

    banned_df = df[df["confirmed_ban"] == 1]
    banned_ids = banned_df["reported_ids"].tolist()

    total_xp_sql = '''
        SELECT
            SUM(total) as total_xp
        FROM playerHiscoreDataLatest
        WHERE Player_id IN :banned_ids
    '''

    total_xp_data = SQL.execute_sql(sql=total_xp_sql, param={"banned_ids": banned_ids})

    try:
        df_detect_manual = df.loc[df['detect'] == 1]

        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_manual['possible_ban'].sum()),
            "incorrect_reports": int(df_detect_manual['confirmed_player'].sum())
        }

        manual_dict["possible_bans"] = manual_dict["possible_bans"] - manual_dict["bans"]

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
            "reports": total_subs - manual_dict["reports"],
            "bans": int(df_detect_passive['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_passive['possible_ban'].sum())
        }

        passive_dict["possible_bans"] = passive_dict["possible_bans"] - passive_dict["bans"]

    except KeyError:
        passive_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0
        }

    total_dict = {
        "reports": total_subs,
        "bans": passive_dict['bans'] + manual_dict['bans'],
        "possible_bans": passive_dict['possible_bans'] + manual_dict['possible_bans'],
        "feedback": len(pd.DataFrame(SQL.get_total_feedback_submissions(contributors)).index),
        "total_xp_removed": float(total_xp_data[0].total_xp)
    }

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

