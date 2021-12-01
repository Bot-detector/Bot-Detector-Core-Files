import time
from typing import List, Optional

from api.database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter
from pydantic import BaseModel

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

async def batch_function(function, data, batch_size=10):
    for i in range(0, len(data), batch_size):
        logger.debug(f'batch: {function.__name__}, {i}/{len(data)}')
        batch = data[i:i+batch_size]
        await function(batch)
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
    await batch_function(sql_update_players, players, batch_size=500)

    # stop if there are no hiscores to insert
    if not hiscores:
        return {'ok':'ok'}
    
    # insert many into hiscores
    await batch_function(sql_insert_hiscores, hiscores, batch_size=500)
    return {'ok':'ok'}
    
