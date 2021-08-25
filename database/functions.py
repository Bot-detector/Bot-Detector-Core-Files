import logging
from collections import namedtuple

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .database import engine


def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list
    
async def execute_sql(sql, param={}, debug=False, engine=engine, row_count=100_000, page=1):
    has_return = True if sql.strip().lower().startswith('select') else False
    
    if has_return:
        # add pagination to every query
        # max number of rows = 100k
        row_count = row_count if row_count <= 100_000 else 100_000
        offset = (page - 1)*row_count
        # add limit to sql
        sql = f'{sql} limit :offset, :row_count'
        # add the param
        param['offset'] = offset
        param['row_count'] = row_count
    
    # parsing
    sql = text(sql)

    # debugging
    if debug:
        logging.debug(f'{has_return=}')
        logging.debug(f'sql={sql.compile(engine)}')
        logging.debug(f'{param=}')
    
    # with handles open and close connection
    async with engine.connect() as conn:
        # creates thread save session
        Session = sessionmaker(conn, class_=AsyncSession)
        async with Session() as session:
            # execute session
            rows = await session.execute(sql, param)
            # parse data
            records = sql_cursor(rows) if has_return else None
            await session.commit()
     # make sure that we dont use another engine
    await engine.dispose()
    return records

class sql_cursor:
    def __init__(self, rows):
        self.rows = rows

    def rows2dict(self):
        return self.rows.mappings().all()

    def rows2tuple(self):
        Record = namedtuple('Record', self.rows.keys())
        return [Record(*r) for r in self.rows.fetchall()]

class sqlalchemy_result:
    def __init__(self, rows):
        self.rows = [row[0] for row in rows]

    def rows2dict(self):
        return [{col.name: getattr(row, col.name) for col in row.__table__.columns} for row in self.rows]

    def rows2tuple(self):
        columns = [col.name for col in self.rows[0].__table__.columns]
        Record = namedtuple('Record', columns)
        return [Record(*[getattr(row, col.name) for col in row.__table__.columns]) for row in self.rows]

async def verify_token(token:str, verifcation:str) -> bool:
    sql = 'select * from Tokens where token=:token'
    param = {'token': token}
    data = await execute_sql(sql, param=param, debug=False)
    player_token = data.rows2tuple()

    # default no permissions
    perm = False 

    # check if token exists (empty list if token does not exist)
    if not player_token:
        raise HTTPException(status_code=404, detail=f"insufficient permissions: {verifcation}")

    # all possible checks
    permissions = {
        'hiscore': player_token[0].request_highscores,
        'ban':player_token[0].verify_ban,
        'create_token': player_token[0].create_token,
        'verify_players': player_token[0].verify_players
    }

    if permissions.get(verifcation, 0) == 1:
        perm = True
    else:
        raise HTTPException(status_code=404, detail=f"insufficient permissions: {verifcation}")
    return perm
