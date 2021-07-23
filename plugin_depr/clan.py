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

    players = df['player'].to_list()

    kc_data = []

    for player in players:
        other_names_data = SQL.get_other_linked_accounts(player)
        if len(other_names_data) > 1:
            other_names = [r.name for r in other_names_data]
        else:
            other_names = [player]

        combined_kc_data = SQL.get_contributions(other_names)
        df_combined = pd.DataFrame(combined_kc_data)
        df_combined = df_combined.drop_duplicates(inplace=False, subset=["reported_ids", "detect"], keep="last")

        if not df_combined.empty:
            total_bans = df_combined["confirmed_ban"].sum()
        else:
            total_bans = 0

        kc_data.append([player, total_bans])

   
    df_kc = pd.DataFrame(kc_data, columns=["name", "kc"]) 

    df = pd.merge(df,df_kc, left_on='player', right_on='name')


    mask = (df['rank'] == 'CLAN_RANK_1')
    df = df[mask]
    df['rank'] = 'CLAN_RANK_2'

    # format data
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))
