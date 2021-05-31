import pandas as pd
import SQL
from flask import Blueprint, json, request, jsonify

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
    r = [
        {
            'player': 'extreme4all',
            'rank': 'OWNER'
        },
        {
            'player': 'cyborger',
            'rank': 'OWNER'
        },
        {
            'player': 'ferrariic',
            'rank': 'CLAN_RANK_1'
        }
    ]
    return jsonify(r)