from typing import Optional

from src.database.functions import PLAYERDATA_ENGINE
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import EngineType
from src.database.functions import sqlalchemy_result, verify_token
from src.database.models import (
    Player,
    PlayerHiscoreDataLatest,
    PlayerHiscoreDataXPChange,
    playerHiscoreData,
)
from src.utils import logging_helpers
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select

router = APIRouter()


class hiscore(BaseModel):
    """
    Hiscore entry data
    """

    Player_id: int
    total: int
    attack: int
    defence: int
    strength: int
    hitpoints: int
    ranged: int
    prayer: int
    magic: int
    cooking: int
    woodcutting: int
    fletching: int
    fishing: int
    firemaking: int
    crafting: int
    smithing: int
    mining: int
    herblore: int
    agility: int
    thieving: int
    slayer: int
    farming: int
    runecraft: int
    hunter: int
    construction: int
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
    nex: int
    obor: int
    phantom_muspah: int
    phosanis_nightmare: int
    sarachnis: int
    scorpia: int
    skotizo: int
    tempoross: int
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    theatre_of_blood_hard: int
    thermonuclear_smoke_devil: int
    tombs_of_amascut: int
    tombs_of_amascut_expert: int
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int


@router.get("/hiscore/", tags=["Hiscore"])
async def get_player_hiscore_data(
    token: str,
    request: Request,
    player_id: int = Query(..., ge=0),
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1),
):
    """
    Select daily scraped hiscore data, by player_id
    """
    # verify token
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    # query
    table = playerHiscoreData
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    # paging
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/hiscore/Latest", tags=["Hiscore"])
async def get_latest_hiscore_data_for_an_account(
    token: str, request: Request, player_id: int = Query(..., ge=0)
):
    """
    Select the latest hiscore of a player.
    """
    # verify token
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    # query
    table = PlayerHiscoreDataLatest
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/hiscore/Latest/bulk", tags=["Hiscore"])
async def get_latest_hiscore_data_by_player_features(
    token: str,
    request: Request,
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1),
    possible_ban: Optional[int] = Query(None, ge=0, le=1),
    confirmed_ban: Optional[int] = Query(None, ge=0, le=1),
    confirmed_player: Optional[int] = Query(None, ge=0, le=1),
    label_id: Optional[int] = Query(None, ge=0),
    label_jagex: Optional[int] = Query(None, ge=0, le=5),
    greater_than: Optional[int] = Query(None, ge=0),
):
    """
    Select the latest hiscore data of multiple players by filtering on the player features.
    """
    # verify token
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    if (
        None
        == possible_ban
        == confirmed_ban
        == confirmed_player
        == label_id
        == label_jagex
        == greater_than
    ):
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

    if not greater_than is None:
        sql = sql.where(Player.id >= greater_than)

    # paging
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # join
    sql = sql.join(Player)

    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/hiscore/XPChange", tags=["Hiscore"])
async def get_account_hiscore_xp_change(
    token: str,
    request: Request,
    player_id: int = Query(..., ge=0),
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1),
):
    """
    Select daily scraped differential in hiscore data by Player ID
    """
    # verify token
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    # query
    table = PlayerHiscoreDataXPChange
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    # paging
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/hiscore", tags=["Hiscore"])
async def post_hiscore_data_to_database(
    hiscores: hiscore, token: str, request: Request
):
    """
    Insert hiscore data.
    """
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    values = hiscores.dict()

    # query
    table = playerHiscoreData
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
