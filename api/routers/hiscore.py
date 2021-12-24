from typing import Optional

from api.database.database import EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import (PlayerHiscoreDataLatest,
                                 PlayerHiscoreDataXPChange, playerHiscoreData, Player)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select

router = APIRouter()


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
    tempoross: int
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
    token: str,
    player_id: int,
    row_count: int = 100_000,
    page: int = 1
):
    '''
        Selects stored hiscore data for a player.
    '''
    # verify token
    await verify_token(token, verifcation='ban')

    # query
    table = playerHiscoreData
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/Latest", tags=["hiscore"])
async def get(
    token: str,
    player_id: int
):
    '''
        Select the latest hiscore of a player.
    '''
    # verify token
    await verify_token(token, verifcation='ban')

    # query
    table = PlayerHiscoreDataLatest
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/Latest/bulk", tags=["hiscore"])
async def get_hiscore_latest_bulk(
    token: str,
    row_count: int = 100_000,
    page: int = 1,
    possible_ban: Optional[int] = None,
    confirmed_ban: Optional[int] = None,
    confirmed_player: Optional[int] = None,
    label_id: Optional[int] = None,
    label_jagex: Optional[int] = None,
):
    '''
        Select latest bulk hiscore data.
    '''
    # verify token
    await verify_token(token, verifcation='ban')

    if None == possible_ban == confirmed_ban == confirmed_player == label_id == label_jagex:
        raise HTTPException(status_code=404, detail="No param given")

    # query
    sql = select(PlayerHiscoreDataLatest)

    # filters
    if not possible_ban is None:
        sql = sql.where(Player.possible_ban == possible_ban)

    if not confirmed_ban is None:
        sql = sql.where(Player.confirmed_ban == confirmed_ban)

    if not confirmed_player is None:
        sql = sql.where(Player.confirmed_player == confirmed_player)

    if not label_id is None:
        sql = sql.where(Player.label_id == label_id)

    if not label_jagex is None:
        sql = sql.where(Player.label_jagex == label_jagex)

    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # join
    sql = sql.join(Player)

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/XPChange", tags=["hiscore"])
async def get(
    token: str,
    player_id: int,
    row_count: int = 100_000,
    page: int = 1
):
    '''
        Selects player's XP change data.
    '''
    # verify token
    await verify_token(token, verifcation='ban')

    # query
    table = PlayerHiscoreDataXPChange
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/hiscore", tags=["hiscore"])
async def post(hiscores: hiscore, token: str):
    '''
        Inserts hiscore data from the OSRS hiscores API to the Database.
    '''
    await verify_token(token, verifcation='ban')

    values = hiscores.dict()

    # query
    table = PlayerHiscoreDataXPChange
    sql_insert = insert(table).values(values)
    sql_insert = sql_insert.prefix_with('ignore')

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {'ok': 'ok'}
