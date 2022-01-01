import time
from typing import List, Optional

from api.database.database import Engine, EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import Player as dbPlayer
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select, update

router = APIRouter()


class Player(BaseModel):
    player_id: int
    name: Optional[str]
    possible_ban: Optional[bool]
    confirmed_ban: Optional[bool]
    confirmed_player: Optional[bool]
    label_id: Optional[int]
    label_jagex: Optional[int]


@router.get("/v1/player", tags=["Player"])
async def get_player_information(
    token: str,
    player_name: Optional[str] = None,
    player_id: Optional[int] = Query(None, ge=0),
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1)
):
    '''
        Select a player by name or id.
    '''
    await verify_token(token, verification='request_highscores', route='[GET]/v1/player')

    # return exception if no param are given
    if None == player_name == player_id:
        raise HTTPException(status_code=404, detail="No valid parameters given")

    # create query
    sql = select(dbPlayer)

    # filters
    if not player_name == None:
        sql = sql.where(dbPlayer.name == player_name)
    if not player_id == None:
        sql = sql.where(dbPlayer.id == player_id)

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/player/banned-accounts", tags=["Player"])
async def get_banned_player_names(
    token: str,
    player_name: Optional[str] = None,
    player_id: Optional[int] = Query(None, ge=0),
    row_count: int = Query(200, ge=1, le=200),
    page: int = Query(1, ge=1)
):
    '''
        Select a player by name or id.
    '''
    await verify_token(token, verification='request_highscores', route='[GET]/v1/player/banned-accounts')

    # create query
    sql = select(dbPlayer)

    # filters
    sql = sql.where(dbPlayer.confirmed_ban == 1)
    
    if not player_name == None:
        sql = sql.where(dbPlayer.name == player_name)
    if not player_id == None:
        sql = sql.where(dbPlayer.id == player_id)

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))
    sql = sql.order_by(dbPlayer.name)
    
    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/player/bulk", tags=["Player"])
async def get_bulk_player_data_from_the_plugin_database(
    token: str,
    possible_ban: Optional[int] = None,
    confirmed_ban: Optional[int] = None,
    confirmed_player: Optional[int] = None,
    label_id: Optional[int] = None,
    label_jagex: Optional[int] = None,
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1)
    ):
    '''
        Selects bulk player data from the plugin database.
    '''
    await verify_token(token, verification='request_highscores', route='[POST]/v1/player')

    # return exception if no param are given
    if None == possible_ban == confirmed_ban == confirmed_player == label_id == label_jagex:
        raise HTTPException(status_code=404, detail="No param given")

    # create query
    sql = select(dbPlayer)

    # filters    
    # filters
    if not possible_ban is None:
        sql = sql.where(dbPlayer.possible_ban == possible_ban)

    if not confirmed_ban is None:
        sql = sql.where(dbPlayer.confirmed_ban == confirmed_ban)

    if not confirmed_player is None:
        sql = sql.where(dbPlayer.confirmed_player == confirmed_player)

    if not label_id is None:
        sql = sql.where(dbPlayer.label_id == label_id)

    if not label_jagex is None:
        sql = sql.where(dbPlayer.label_jagex == label_jagex)

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/v1/player", tags=["Player"])
async def update_existing_player_data(player: Player, token: str):
    '''
        Update player & return updated player.
    '''
    await verify_token(token, verification='verify_ban')

    # param
    param = player.dict()
    param['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    player_id = param.pop('player_id')

    # sql
    sql_update = update(dbPlayer)
    sql_update = sql_update.values(param)
    sql_update = sql_update.where(dbPlayer.id == player_id)

    sql_select = select(dbPlayer)
    sql_select = sql_select.where(dbPlayer.id == player_id)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_update)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/player", tags=["Player"])
async def insert_new_player_data_into_plugin_database(player_name: str, token: str):
    '''
        Insert new player & return player.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/player')

    sql_insert = insert(dbPlayer)
    sql_insert = sql_insert.values(name=player_name)
    sql_insert = sql_insert.prefix_with('ignore')

    sql_select = select(dbPlayer)
    sql_select = sql_select.where(dbPlayer.name == player_name)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()
