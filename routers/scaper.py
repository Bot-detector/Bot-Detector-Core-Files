import time
from re import I
from typing import List, Optional

import Config
import pandas as pd
import SQL
from database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter, status
from pydantic import BaseModel

import routers.hiscore as hi
from routers.hiscore import hiscore
from routers.player import Player

router = APIRouter()

class scraper(BaseModel):
    hiscore: hiscore
    player: Player

async def sql_get_players_to_scrape(page=1, amount=100):
    sql = 'select * from playersToScrape WHERE length(name) <= 12 ORDER BY RAND()'
    data = await execute_sql(sql, page=page, row_count=amount)
    return data.rows2dict

@router.get("/scraper/players/{page}/{amount}/{token}", tags=["scraper"])
async def get_players_to_scrape(token, page=None, amount=None):
    await verify_token(token, verifcation='ban')
    return await sql_get_players_to_scrape(page=page, amount=amount)

async def sql_update_player(player_id, possible_ban=None, confirmed_ban=None, confirmed_player=None, label_id=None, label_jagex=None, debug=False):
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    param = {
        'updated_at':       time_now,
        'possible_ban':     possible_ban,
        'confirmed_ban':    confirmed_ban,
        'confirmed_player': confirmed_player,
        'label_id':         label_id,
        'player_id':        player_id,
        'label_jagex':      label_jagex
    }
    
    values = []
    for column in list(param.keys()):
        if column != 'player_id' and param[column] != None:
            values.append(f'{column}=:{column}')

    values = list_to_string(values)

    sql_update = (f'''
        update Players 
        set
            {values}
        where 
            id=:player_id
        ''')
    
    await execute_sql(sql_update, param=param)
    return

async def sql_insert_highscore(player_id, skills, minigames):
    keys = []
    keys.append('player_id')
    keys.extend(list(skills.keys()))
    keys.extend(list(minigames.keys()))

    values = []
    values.append(player_id)
    values.extend(list(skills.values()))
    values.extend(list(minigames.values()))

    columns = list_to_string(keys)
    values = list_to_string(values)

    # f string is not so secure but we control the skills & minigames dict
    sql_insert = f"insert ignore into playerHiscoreData ({columns}) values ({values});"
    await execute_sql(sql_insert, param={})
    return

async def process_player(player, hiscore):
    # update player in Players
    await sql_update_player(
        player_id= player['id'], 
        possible_ban=player['possible_ban'], 
        confirmed_ban=player['confirmed_ban'], 
        confirmed_player=player['confirmed_player'], 
        # label_id=player['label_id'], 
        label_jagex=player['label_jagex']
    )
    if hiscore is not None:
        # parse data
        skills = {d:hiscore[d] for d in hiscore if d in hi.skills.__dict__.keys()}
        minigames = {d:hiscore[d] for d in hiscore if d in hi.minigames.__dict__.keys()}
        # insert into hiscores
        await sql_insert_highscore(
            player_id=player['id'], 
            skills=skills, 
            minigames=minigames
        )
        # make ml prediction
        # Config.sched.add_job(model.predict_model ,args=[player['name'], 0, 100_000, Config.use_pca, True], replace_existing=False, name='scrape-predict')
        del skills, minigames
    del player, hiscore
    return



@router.post("/scraper/hiscores/{token}", tags=["scraper"])
async def post_hiscores_to_db(token, data: List[scraper]):
    await verify_token(token, verifcation='ban')

    data = [d.__dict__ for d in data]
    data = [
        {
            'player': d['player'].__dict__,
            'hiscore': d['hiscore'].__dict__
        } for d in data
    ]

    for d in data:
        Config.sched.add_job(process_player ,args=[d['player'], d['hiscore']], replace_existing=False, name=f'scrape_{d["player"]["name"]}')
    del data
    return {'OK':'OK'}
