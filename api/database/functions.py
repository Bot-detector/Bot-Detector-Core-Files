import asyncio
import logging
import random
import traceback
from collections import namedtuple

from api.database.database import Engine, EngineType
from api.database.models import Token
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy.sql.expression import select

logger = logging.getLogger(__name__)

def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list
    
async def execute_sql(sql, param={}, debug=False, engine_type=EngineType.PLAYERDATA, row_count=100_000, page=1, is_retry=False, has_return=None):

    engine = Engine(engine_type)

    if not is_retry:
        has_return = True if sql.strip().lower().startswith('select') else False
    
        if has_return:
            # add pagination to every query
            # max number of rows = 100k
            row_count = row_count if row_count <= 100_000 else 100_000
            page = page if page >= 1 else 1
            offset = (page - 1)*row_count
            # add limit to sql
            sql = f'{sql} limit :offset, :row_count;'
            # add the param
            param['offset'] = offset
            param['row_count'] = row_count
        
        # parsing
        sql = text(sql)

    # debugging
    if debug:
        logger.debug(f'{has_return=}')
        logger.debug(f'sql={sql.compile(engine.engine)}')
        logger.debug(f'{param=}')
    
    try:
        async with engine.session() as session:
            # execute session
            rows = await session.execute(sql, param)
            # parse data
            records = sql_cursor(rows) if has_return else None
            # commit session
            await session.commit()
        # clean up connection
        await engine.engine.dispose()

    # OperationalError = Deadlock, InternalError = lock timeout
    except OperationalError as e:
        e = '' if debug else e
        logger.debug(f'Deadlock, retrying {e}')
        await asyncio.sleep(random.uniform(0.1,1.1))
        await engine.engine.dispose()
        records = await execute_sql(sql, param, debug, engine_type, row_count, page, is_retry=True, has_return=has_return)
    except InternalError as e:
        e = '' if debug else e
        logger.debug(f'Deadlock, retrying: {e}')
        await asyncio.sleep(random.uniform(0.1,1.1))
        await engine.engine.dispose()
        records = await execute_sql(sql, param, debug, engine_type, row_count, page, is_retry=True, has_return=has_return)
    except Exception as e:
        logger.error('got an unkown error')
        logger.error(traceback.print_exc())
        await engine.engine.dispose()
        records = None
    
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
    # query
    sql = select(Token)
    sql = sql.where(Token.token==token)

    engine = Engine(EngineType.PLAYERDATA)

    # transaction
    async with engine.session() as session:
        data = await session.execute(sql)
    
    # parse data
    data = sqlalchemy_result(data)

    if len(data.rows) == 0:
        raise HTTPException(status_code=404, detail=f"insufficient permissions: {verifcation}")

    player_token = data.rows2tuple()

    # check if token exists (empty list if token does not exist)
    if not player_token:
        raise HTTPException(status_code=404, detail=f"insufficient permissions: {verifcation}")

    # all possible checks
    permissions = {
        'hiscore':          player_token[0].request_highscores,
        'ban':              player_token[0].verify_ban,
        'create_token':     player_token[0].create_token,
        'verify_players':   player_token[0].verify_players
    }

    # get permission, default: 0
    if permissions.get(verifcation, 0) == 1:
        return True

    raise HTTPException(status_code=404, detail=f"insufficient permissions: {verifcation}")

async def batch_function(function, data, batch_size=10):
    for i in range(0, len(data), batch_size):
        logger.debug(f'batch: {function.__name__}, {i}/{len(data)}')
        batch = data[i:i+batch_size]
        await function(batch)
    return
