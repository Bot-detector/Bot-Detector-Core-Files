from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.functions import execute_sql

router = APIRouter()


class hiscore(BaseModel):
    '''
    all the hiscore stuf
    '''
    player_id: int
    total: int
    

@router.get("/v1/hiscore/", tags=["hiscore"])
async def get(
    player_name: Optional[str] = None,
    player_id: Optional[int] = None,
    label_id: Optional[int] = None
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

    has_good_param = False
    for k, v in param.items():
        if v is not None:
            sql = f'{sql} and {k} = :{k}'
            has_good_param = True

    if not (has_good_param):
        raise HTTPException(status_code=404, detail="No valid parameters given")

    data = execute_sql(sql, param, debug=True)
    return {'ok': data}

@router.get("/v1/hiscoreLatest", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.get("/v1/hiscoreExpGain", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.post("/v1/hiscore", tags=["hiscore"])
async def post(hiscores:hiscore):
    '''
    insert data into database
    '''
    pass