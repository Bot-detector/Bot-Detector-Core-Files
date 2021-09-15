import os
import sys
import time

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
        return jsonify({})

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df.fillna(0, inplace=True)
    output = df.to_dict('records')

    #return jsonify([{'id': 122716, 'name': 'Seltzer Bro', 'created_at': '2021-03-17 18:56:15', 'updated_at': '2021-09-15 04:13:51', 'possible_ban': 0, 'confirmed_ban': 0, 'confirmed_player': 1, 'label_id': 1, 'label_jagex': 0}])

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
        # bulk predicting, based on hiscores = today and predictions != today should be better
        # Config.sched.add_job(model.predict_model ,args=[player['name'], 0, 100_000, Config.use_pca, True], replace_existing=False, name='scrape-predict')
        del skills, minigames
    del player, hiscore
    return


def process_scrapes(scrape_data):
    players = []
    hiscores = []

    players_columns = "(name, updated_at, possible_ban, confirmed_ban, confirmed_player, label_id, id, label_jagex)"
    hiscores_columns = ""

    for d in scrape_data:
        player = d['player']
        players.append(build_player_string(player))

        hiscore = d['hiscores']
        if hiscore is not None:
            hiscore['Player_id'] = player['id']
            hiscore_separated_data = build_hiscores_strings(hiscore)

            hiscores_columns = hiscore_separated_data["columns"]
            hiscores.append(hiscore_separated_data["values"])

    persist_scrapes(players=players, player_columns=players_columns, hiscores=hiscores, hiscores_columns=hiscores_columns)

    return


def build_player_string(p: dict) -> str:
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    p['updated_at'] = time_now

    return f"(\"{p['name']}\", \"{p['updated_at']}\", {p['possible_ban']}, {p['confirmed_ban']}, {p['confirmed_player']}, {p['label_id']}, {p['id']}, {p['label_jagex']})"


def build_hiscores_strings(hs: dict) -> dict:
    hs_columns_str = "("
    hs_values_str = "("

    columns_list = []
    values_list = []

    for k, v in hs.items():
        columns_list.append(str(k))
        values_list.append(str(v)) 

    hs_columns_str += f"{','.join(columns_list)})"
    hs_values_str += f"{','.join(values_list)})"

    return {"columns": hs_columns_str, "values": hs_values_str}


def persist_scrapes(players, player_columns, hiscores, hiscores_columns):

    if len(hiscores) > 0:
        attempts = 0
        success = False

        while attempts < 3:
            try:
                SQL.insert_multiple_highscores(columns=hiscores_columns, values=hiscores)
                success = True
                break
            except:
                attempts += 1
                time.sleep(10)
        
        if success:
            SQL.update_multiple_players(columns=player_columns, values=players)

    else:
        SQL.update_multiple_players(columns=player_columns, values=players)
    return

    
@app_scraper.route("/scraper/hiscores/<token>", methods=['POST'])
def post_hiscores_to_db(token):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = request.get_json()

    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    Config.sched.add_job(process_scrapes ,args=[data], replace_existing=False, name=f'scrape_{time_now}', misfire_grace_time=None)
        
    del data
    return jsonify({'OK':'OK'})
