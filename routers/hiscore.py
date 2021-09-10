import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.functions import execute_sql, list_to_string
import datetime

router = APIRouter()

class skills(BaseModel):
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

class minigames(BaseModel):
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
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    thermonuclear_smoke_devil: int
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int

class hiscore(BaseModel):
    '''
    all the hiscore stuf
    '''
    player_id: int
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
    

@router.get("/v1/hiscore/", tags=["hiscore"])
async def get(
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
    ):
    '''
    select data from database
    '''
    sql = ('''
        select 
            pl.name, 
            phd.*
        from playerHiscoreData phd
        inner join Players pl on (phd.Player_id = pl.id)
        where 1=1
    ''')

    param = {
        'name': player_name,
        'id': player_id,
        'label_id': label_id
    }

    # build query
    sql_filter = [f' and pl.{k} = :{k}' for k,v in param.items() if v is not None]
    has_good_param = True if len(sql_filter) > 0 else False
    sql = f'{sql} {"".join(sql_filter)}'

    # return exception if no param are given
    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = await execute_sql(sql, param, row_count=row_count, page=page)
    return data.rows2dict()

@router.get("/v1/hiscoreLatest", tags=["hiscore"])
async def get(
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
    ):
    '''
    select data from database
    '''
    sql = ('''
        select 
            pl.name, 
            phd.*
        from playerHiscoreDataLatest phd
        inner join Players pl on (phd.Player_id = pl.id)
        where 1=1
    ''')

    param = {
        'name': player_name,
        'id': player_id,
        'label_id': label_id
    }

    # build query
    sql_filter = [f' and pl.{k} = :{k}' for k,v in param.items() if v is not None]
    has_good_param = True if len(sql_filter) > 0 else False
    sql = f'{sql} {"".join(sql_filter)}'

    # return exception if no param are given
    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = await execute_sql(sql, param, row_count=row_count, page=page)
    return data.rows2dict()

@router.get("/v1/hiscoreXPChange", tags=["hiscore"])
async def get(
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
    ):
    '''
    select data from database
    '''
    sql = ('''
        select 
            pl.name, 
            phd.*
        from playerHiscoreDataXPChange phd
        inner join Players pl on (phd.Player_id = pl.id)
        where 1=1
    ''')

    param = {
        'name': player_name,
        'id': player_id,
        'label_id': label_id
    }

    # build query
    sql_filter = [f' and pl.{k} = :{k}' for k,v in param.items() if v is not None]
    has_good_param = True if len(sql_filter) > 0 else False
    sql = f'{sql} {"".join(sql_filter)}'

    # return exception if no param are given
    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = await execute_sql(sql, param, row_count=row_count, page=page)
    return data.rows2dict()

@router.get("/v1/hiscoreXPChangeLatest", tags=["hiscore"])
async def get(
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
    ):
    '''
    select data from database
    '''
    sql = ('''
        select 
            pl.name, 
            phd.*
        from playerHiscoreDataXPChange phd
        inner join Players pl on (phd.Player_id = pl.id)
        where 1=1
            and ts_date = :ts_date
    ''')

    param = {
        'name': player_name,
        'id': player_id,
        'label_id': label_id,
        'ts_date': datetime.datetime.now().strftime('%Y-%m-%d')
    }

    # build query
    sql_filter = [f' and {k} = :{k}' for k,v in param.items() if v is not None or k != 'ts_date']
    has_good_param = True if len(sql_filter) > 0 else False
    sql = f'{sql} {"".join(sql_filter)}'

    # return exception if no param are given
    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = await execute_sql(sql, param, row_count=row_count, page=page)
    return data.rows2dict()

@router.post("/v1/hiscore", tags=["hiscore"])
async def post(hiscores: hiscore):
    '''
    insert data into database
    '''
    param = hiscores.dict()
    # list of column values
    columns = list_to_string(list(param.keys()))
    values = list_to_string([f':{column}' for column in list(param.keys())])

    sql = f'insert ignore into playerHiscoreData ({columns}) values ({values});'
    await execute_sql(sql, param)
    return {'ok':'ok'}