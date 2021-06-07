import json

import pandas as pd
import SQL
from flask import Blueprint, json, jsonify, request

clan = Blueprint('clan', __name__, template_folder='templates')

@clan.route('/<version>/plugin/clan/rank-update/<token>', methods=['POST'])
def get_clan_rank(version, token):
    '''
        receive a dictionary of
        [
            {
                'player':'',
                'rank':''
            }, ...
        ]
        return the same dictionary with the players that have incorrect rank (the returned rank is the correct rank)
    '''
    user_ranks = request.get_json()
    df = pd.DataFrame(user_ranks)


    # get KC of players
    players = df['player'].to_list()

    df_kc = SQL.get_player_kc(players)
    df_kc = pd.DataFrame(df_kc)

    df = pd.merge(df,df_kc, left_on='player', right_on='name')

    for player in players:
        other_names_data = SQL.get_other_linked_accounts(player)
        other_names = [r.name for r in other_names_data]

        if len(other_names) > 1:

            combined_kc_data = SQL.get_contributions(other_names)
            df_kc = pd.DataFrame(combined_kc_data)
            df_kc = df_kc.drop_duplicates(inplace=False, subset=["reported_ids", "detect"], keep="last")
            total_bans = df_kc["confirmed_ban"].sum()
            
            df.loc[(df.name == player), "kc"] = total_bans


    mask = (df['rank'] == 'CLAN_RANK_1')
    df = df[mask]
    df['rank'] = 'CLAN_RANK_2'

    # format data
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))
