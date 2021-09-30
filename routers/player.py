import time
from typing import List, Optional

from database.database import async_session
from database.functions import execute_sql, sqlalchemy_result, verify_token
from database.models import Player as dbPlayer
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select, update

router = APIRouter()


class Name(BaseModel):
    name: str


class NamesList(BaseModel):
    names: List[Name]


class Player(BaseModel):
    player_id: int
    name: Optional[str]
    possible_ban: Optional[bool]
    confirmed_ban: Optional[bool]
    confirmed_player: Optional[bool]
    label_id: Optional[int]
    label_jagex: Optional[int]


@router.get("/v1/player", tags=["player"])
async def get(
    token: str,
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='hiscore')

    # return exception if no param are given
    if None == player_name == player_id == label_id:
        raise HTTPException(
            status_code=404, detail="No valid parameters given")

    # create query
    sql = select(dbPlayer)

    # filters
    if not player_name == None:
        sql = sql.where(dbPlayer.name == player_name)

    if not player_id == None:
        sql = sql.where(dbPlayer.id == player_id)

    if not label_id == None:
        sql = sql.where(dbPlayer.label_id == label_id)

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # transaction
    async with async_session() as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/player/bulk", tags=["player"])
async def post_bulk(
    token: str,
    player_name: Optional[List[str]] = None,
    player_id: Optional[List[int]] = None,
    row_count: int = 100_000,
    page: int = 1
):
    '''
        select data from database
    '''
    await verify_token(token, verifcation='hiscore')

    # return exception if no param are given
    if None == player_name == player_id:
        raise HTTPException(
            status_code=404, detail="No valid parameters given")

    # create query
    sql = select(dbPlayer)

    # filters
    if not player_name == None:
        sql = sql.where(dbPlayer.name.in_(player_name))

    if not player_id == None:
        sql = sql.where(dbPlayer.id.in_(player_id))

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # transaction
    async with async_session() as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/v1/player", tags=["player"])
async def put(player: Player, token: str):
    '''
    update data into database
    '''
    await verify_token(token, verifcation='hiscore')

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
    async with async_session() as session:
        await session.execute(sql_update)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/player", tags=["player"])
async def post(player_name: str, token: str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='hiscore')

    sql_insert = insert(dbPlayer)
    sql_insert = sql_insert.values(name=player_name)
    sql_insert = sql_insert.prefix_with('ignore')

    sql_select = select(dbPlayer)
    sql_select = sql_select.where(dbPlayer.name == player_name)

    # transaction
    async with async_session() as session:
        await session.execute(sql_insert)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/bulk_players", tags=["player"])
async def get_bulk(player_names: NamesList, token: str):
    await verify_token(token, verifcation='hiscore')

    names = [name_entry.name for name_entry in player_names.names]

    sql = 'select * from Players where name in :names'

    param = {
        'names': names
    }

    data = await execute_sql(sql, param)
    return data.rows2dict()
