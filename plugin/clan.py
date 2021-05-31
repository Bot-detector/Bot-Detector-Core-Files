import json

import pandas as pd
import SQL
from flask import Blueprint, json, jsonify, request

clan = Blueprint('clan', __name__, template_folder='templates')


@clan.route('/<version>/plugin/clan/rank-update/<token>', methods=['POST'])
def get_clan_rank(version, token):
    '''
        receive a dictionary of
        [{
            'player':'',
            'rank':''
        }, ...
        ]
        return the same dictionary with the players that have incorrect rank (the returned rank is the correct rank)
    '''
    user_ranks = request.get_json()
    df = pd.DataFrame(user_ranks)

    #TODO
    # get KC of players

    # parse KC of players

    # return players with their new rank

    # sample code
    mask = (df['rank'] == 'CLAN_RANK_1')
    df = df[mask]
    df['rank'] = 'CLAN_RANK_2'

    # format data
    myjson = df.to_json(orient='records')

    return jsonify(json.loads(myjson))
