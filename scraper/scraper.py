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

    if df.empty:
        return jsonify([])

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df.fillna(0, inplace=True)
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
    if hiscore is not None:
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
        Config.sched.add_job(model.predict_model ,args=[player['name'], 0, 100_000, Config.use_pca, True], replace_existing=False, name='scrape-predict')
    return

@app_scraper.route("/scraper/hiscores/<token>", methods=['POST'])
def post_hiscores_to_db(token):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = request.get_json()

    print(len(data))

    for i, d in enumerate(data):
        Config.sched.add_job(process_player ,args=[d['player'], d['hiscores']], replace_existing=False, name=f'scrape_{d["player"]["name"]}')
        
    return jsonify({'OK':'OK'})
