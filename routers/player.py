import time
from typing import Optional, List

from database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    sql ='select * from Players where 1=1'
    param = {
        'name': player_name,
        'id': player_id,
        'label_id': label_id
    }

    # build query
    sql_filter = [f' and {k} = :{k}' for k,v in param.items() if v is not None]
    has_good_param = True if len(sql_filter) > 0 else False
    sql = f'{sql} {"".join(sql_filter)}'

    # return exception if no param are given
    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = await execute_sql(sql, param, row_count=row_count, page=page)
    return data.rows2dict()

@router.put("/v1/player", tags=["player"])
async def put(player: Player, token: str):
    '''
    update data into database
    '''
    await verify_token(token, verifcation='hiscore')
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    param = player.dict()
    param['updated_at'] = time_now

    exclude = ['player_id', 'name']
    values = [f'{k}=:{k}' for k,v in param.items() if v is not None and k not in exclude]
    values = list_to_string(values)

    sql = (f'''
        update Players 
        set
            {values}
        where 
            id=:player_id;
    ''')
    select = "select * from Players where id=:player_id"

    await execute_sql(sql, param)
    data = await execute_sql(select, param)
    return data.rows2dict()

@router.post("/v1/player", tags=["player"])
async def post(player_name: str, token: str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='hiscore')
    sql = "insert ignore into Players (name) values(:player_name);"
    select = "select * from Players where name=:player_name"

    param = {
        'player_name': player_name
    }

    await execute_sql(sql, param)
    data = await execute_sql(select, param)
    return data.rows2dict()


@router.get("/v1/bulk_players", tags=["player"])
async def get_bulk(player_names: NamesList, token: str):
    await verify_token(token, verifcation='hiscore')

    names = [name_entry.name for name_entry in player_names.names]

    sql ='select * from Players where name in :names'

    param = {
        'names': names
    }

    data = await execute_sql(sql, param)
    return data.rows2dict()