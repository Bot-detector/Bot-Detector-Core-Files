import asyncio
import logging
import random
import re
import traceback
from asyncio.tasks import create_task
from collections import namedtuple

# Although never directly used, the engines are imported to add a permanent reference
# to these entities to prevent the
# garbage collector from trying to dispose of our engines.
from api.database.database import (DISCORD_ENGINE, PLAYERDATA_ENGINE, Engine,
                                   EngineType, get_session)
from api.database.models import Token
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy.sql.expression import select

logger = logging.getLogger(__name__)


def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list


async def execute_sql(sql, param={}, debug=False, engine_type=EngineType.PLAYERDATA, row_count=100_000, page=1, is_retry=False, has_return=None, retry_attempt=0):
    # retry breakout
    if retry_attempt >= 5:
        logger.debug(f'To many retries')
        return None

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
        engine = Engine(engine_type)
        logger.debug(f'{has_return=}')
        logger.debug(f'sql={sql.compile(engine)}')
        logger.debug(f'{param=}')

        await engine.engine.dispose()

    try:
        async with get_session(engine_type) as session:
            # execute session
            rows = await session.execute(sql, param)
            # parse data
            records = sql_cursor(rows) if has_return else None
            # commit session
            await session.commit()

    # OperationalError = Deadlock, InternalError = lock timeout
    except OperationalError as e:
        e = e if debug else ''
        logger.debug(f'Deadlock, retrying {e}')
        await asyncio.sleep(random.uniform(0.1, 1.1))
        records = await execute_sql(sql, param, debug, engine_type, row_count, page, is_retry=True, has_return=has_return, retry_attempt=retry_attempt+1)
    except InternalError as e:
        e = e if debug else ''
        logger.debug(f'Lock, retrying: {e}')
        await asyncio.sleep(random.uniform(0.1, 1.1))
        records = await execute_sql(sql, param, debug, engine_type, row_count, page, is_retry=True, has_return=has_return, retry_attempt=retry_attempt+1)
    except Exception as e:
        logger.error('got an unkown error')
        logger.error(traceback.print_exc())
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


async def verify_token(token: str, verifcation: str) -> bool:
    # query
    sql = select(Token)
    sql = sql.where(Token.token == token)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    # parse data
    data = sqlalchemy_result(data)

    if len(data.rows) == 0:
        raise HTTPException(
            status_code=403, detail=f"insufficient permissions: {verifcation}")

    player_token = data.rows2tuple()

    # check if token exists (empty list if token does not exist)
    if not player_token:
        raise HTTPException(
            status_code=403, detail=f"insufficient permissions: {verifcation}")

    # all possible checks
    permissions = {
        'hiscore':          player_token[0].request_highscores,
        'ban':              player_token[0].verify_ban,
        'create_token':     player_token[0].create_token,
        'verify_players':   player_token[0].verify_players
    }

    # get permission, default: 0
    if not permissions.get(verifcation, 0) == 1:
        raise HTTPException(
            status_code=403, detail=f"insufficient permissions: {verifcation}")
    return True


async def batch_function(function, data, batch_size=100):
    batches = []
    for i in range(0, len(data), batch_size):
        logger.debug(f'batch: {function.__name__}, {i}/{len(data)}')
        batch = data[i:i+batch_size]
        batches.append(batch)

    await asyncio.gather(*[
        create_task(function(batch)) for batch in batches
    ])

    return


async def is_valid_rsn(rsn: str) -> bool:
    return re.fullmatch('[\w\d\s_-]{1,13}', rsn)


async def to_jagex_name(name: str) -> str:
    return name.lower().replace('_', ' ').replace('-', ' ').strip()
