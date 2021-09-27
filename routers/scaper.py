import time
from typing import List, Optional

from database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import asyncio
import Config

router = APIRouter()

class hiscore(BaseModel):
    player_id: Optional[int]
    total: int
    Attack: int
    Defence: int
    Strength: int
    Hitpoints: int
    Ranged: int
    Prayer: int
    Magic: int
    Cooking: int
    Woodcutting: int
    Fletching: int
    Fishing: int
    Firemaking: int
    Crafting: int
    Smithing: int
    Mining: int
    Herblore: int
    Agility: int
    Thieving: int
    Slayer: int
    Farming: int
    Runecraft: int
    Hunter: int
    Construction: int
    league: int
    bounty_hunter_hunter: int
    bounty_hunter_rogue: int
    cs_all: int
    cs_beginner: int
    cs_easy: int
    cs_medium: int
    cs_hard: int
    cs_elite: int
    cs_master: int
    lms_rank: int
    soul_wars_zeal: int
    abyssal_sire: int
    alchemical_hydra: int
    barrows_chests: int
    bryophyta: int
    callisto: int
    cerberus: int
    chambers_of_xeric: int
    chambers_of_xeric_challenge_mode: int
    chaos_elemental: int
    chaos_fanatic: int
    commander_zilyana: int
    corporeal_beast: int
    crazy_archaeologist: int
    dagannoth_prime: int
    dagannoth_rex: int
    dagannoth_supreme: int
    deranged_archaeologist: int
    general_graardor: int
    giant_mole: int
    grotesque_guardians: int
    hespori: int
    kalphite_queen: int
    king_black_dragon: int
    kraken: int
    kreearra: int
    kril_tsutsaroth: int
    mimic: int
    nightmare: int
    obor: int
    sarachnis: int
    scorpia: int
    skotizo: int
    tempoross:int
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    theatre_of_blood_hard: int
    thermonuclear_smoke_devil: int
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int

class Player(BaseModel):
    id: int
    name: Optional[str]
    possible_ban: Optional[bool]
    confirmed_ban: Optional[bool]
    confirmed_player: Optional[bool]
    label_id: Optional[int]
    label_jagex: Optional[int]

class scraper(BaseModel):
    hiscores: Optional[hiscore]
    player: Player

async def sql_get_players_to_scrape(page=1, amount=100_000):
    sql = 'select * from playersToScrape WHERE length(name) <= 12 ORDER BY RAND()'
    data = await execute_sql(sql, page=page, row_count=amount)
    return data.rows2dict()

@router.get("/scraper/players/{page}/{amount}/{token}", tags=["scraper"])
async def get_players_to_scrape(token, page:int=1, amount:int=100_000):
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

async def sql_update_players(players):
    values = [f'{c}=:{c}' for c in players[0].keys()]
    values = list_to_string(values)
    sql = f'update Players set {values} where id = :id'
    await execute_sql(sql, players)
    return

async def sql_insert_hiscores(hiscores):
    values = [f'{c}=:{c}' for c in hiscores[0].keys()]
    values = list_to_string(values)
    columns = list_to_string(hiscores[0].keys())
    sql = f'insert ignore into playerHiscoreData ({columns}) values ({values})'
    await execute_sql(sql, hiscores)
    return

@router.post("/scraper/hiscores/{token}", tags=["scraper"])
async def post_hiscores_to_db(token, data: List[scraper]):
    await verify_token(token, verifcation='ban')

    # get all players & all hiscores
    data = [d.dict() for d in data]
    players = []
    hiscores = []
    for d in data:
        player_dict = d['player']
        hiscore_dict = d['hiscores']

        # add extra data
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        player_dict['updated_at'] = time_now
        
        if not hiscore_dict:
            players.append(player_dict)
            continue
        
        hiscore_dict['player_id'] = player_dict['id']

        players.append(player_dict)
        hiscores.append(hiscore_dict)
    
    # update many into players
    await sql_update_players(players)

    # stop if there are no hiscores to insert
    if not hiscores:
        return {'ok':'ok'}
    
    # insert many into hiscores
    await sql_insert_hiscores(hiscores)
    return {'ok':'ok'}
    
