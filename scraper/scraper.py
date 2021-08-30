import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Config
import pandas as pd
import SQL
from flask import Blueprint, config, jsonify, request
from mysite.tokens import verify_token
from Predictions import model

import scraper.extra_data as ed

app_scraper = Blueprint('app_scraper', __name__)


@app_scraper.route("/scraper/players/<token>", methods=['GET'])
@app_scraper.route("/scraper/players/<start>/<amount>/<token>", methods=['GET']) # we could also work with arguments
def get_players_to_scrape(token, start=None, amount=None):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = SQL.get_players_to_scrape(start, amount)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)

def process_player(player, hiscore):
    # update player in Players
    SQL.update_player(
        player_id= player['id'], 
        possible_ban=player['possible_ban'], 
        confirmed_ban=player['confirmed_ban'], 
        confirmed_player=player['confirmed_player'], 
        # label_id=player['label_id'], 
        label_jagex=player['label_jagex']
    )
    # parse data
    skills = {d:hiscore[d] for d in hiscore if d in ed.skills.keys()}
    minigames = {d:hiscore[d] for d in hiscore if d in ed.minigames.keys()}
    # insert into hiscores
    SQL.insert_highscore(
        player_id=player['id'], 
        skills=skills, 
        minigames=minigames
    )
    # make ml prediction
    if hiscore is not None:
        df = model.predict_model(
            player_name=player['name'], 
            use_pca=Config.use_pca, 
            debug=True # force upate
        )
        df['name'] = player['name']
    return

@app_scraper.route("/scraper/hiscores/<token>", methods=['POST'])
def post_hiscores_to_db(token):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404
    data = request.get_json()
    for d in data:
        Config.sched.add_job(process_player ,args=[d['player'], d['hiscores']], replace_existing=False, name='scrape')
        
    return jsonify({'OK':'OK'})
