import asyncio
import logging
import random
import re
import traceback
from asyncio.tasks import create_task
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List

# Although never directly used, the engines are imported to add a permanent reference
# to these entities to prevent the
# garbage collector from trying to dispose of our engines.
from api.database.database import (DISCORD_ENGINE, PLAYERDATA_ENGINE, Engine,
                                   EngineType, get_session)
from api.database.models import ApiPermission, ApiUsage, ApiUser, ApiUserPerm
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy.sql.expression import insert, select

logger = logging.getLogger(__name__)


def list_to_string(l):
    string_list = ", ".join(str(item) for item in l)
    return string_list


async def is_valid_rsn(rsn: str) -> bool:
    return re.fullmatch("[\w\d\s_-]{1,13}", rsn)


async def to_jagex_name(name: str) -> str:
    return name.lower().replace("_", " ").replace("-", " ").strip()


async def jagexify_names_list(names: List[str]) -> List[str]:
    return [await to_jagex_name(n) for n in names if await is_valid_rsn(n)]


async def execute_sql(
    sql,
    param={},
    debug=False,
    engine_type=EngineType.PLAYERDATA,
    row_count=100_000,
    page=1,
    is_retry=False,
    has_return=None,
    retry_attempt=0,
):
    # retry breakout
    if retry_attempt >= 5:
        logger.debug({"message": "Too many retries"})
        return None
    sleep = 5 * retry_attempt

    if not is_retry:
        has_return = True if sql.strip().lower().startswith("select") else False

        if has_return:
            # add pagination to every query
            # max number of rows = 100k
            row_count = row_count if row_count <= 100_000 else 100_000
            page = page if page >= 1 else 1
            offset = (page - 1) * row_count
            # add limit to sql
            sql = f"{sql} limit :offset, :row_count;"
            # add the param
            param["offset"] = offset
            param["row_count"] = row_count

        # parsing
        sql = text(sql)

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
        e = e if debug else ""
        logger.debug(
            {"message": f"Deadlock, Retry Attempt: {retry_attempt}, retrying {e}"}
        )
        await asyncio.sleep(random.uniform(0.1, sleep))
        records = await execute_sql(
            sql,
            param,
            debug,
            engine_type,
            row_count,
            page,
            is_retry=True,
            has_return=has_return,
            retry_attempt=retry_attempt + 1,
        )
    except InternalError as e:
        e = e if debug else ""
        logger.debug(
            {"message": f"Lock, Retry Attempt: {retry_attempt}, retrying: {e}"}
        )
        await asyncio.sleep(random.uniform(0.1, sleep))
        records = await execute_sql(
            sql,
            param,
            debug,
            engine_type,
            row_count,
            page,
            is_retry=True,
            has_return=has_return,
            retry_attempt=retry_attempt + 1,
        )
    except Exception as e:
        logger.error({"message": "Unknown Error", "error": e})
        logger.error(traceback.print_exc())
        records = None

    return records


class sql_cursor:
    def __init__(self, rows):
        self.rows = rows

    def rows2dict(self):
        return self.rows.mappings().all()

    def rows2tuple(self):
        Record = namedtuple("Record", self.rows.keys())
        return [Record(*r) for r in self.rows.fetchall()]


class sqlalchemy_result:
    def __init__(self, rows):
        self.rows = [row[0] for row in rows]

    def rows2dict(self):
        return [
            {col.name: getattr(row, col.name) for col in row.__table__.columns}
            for row in self.rows
        ]

    def rows2tuple(self):
        columns = [col.name for col in self.rows[0].__table__.columns]
        Record = namedtuple("Record", columns)
        return [
            Record(*[getattr(row, col.name) for col in row.__table__.columns])
            for row in self.rows
        ]


async def verify_token(token: str, verification: str, route: str = None) -> bool:
    sql = select(ApiUser)
    sql = sql.where(ApiUser.token == token)
    sql = sql.where(ApiPermission.permission == verification)
    sql = sql.join(ApiUserPerm, ApiUser.id == ApiUserPerm.user_id)
    sql = sql.join(ApiPermission, ApiUserPerm.permission_id == ApiPermission.id)

    sql_usage = select(ApiUsage)
    sql_usage = sql_usage.where(ApiUser.id == ApiUsage.user_id)
    sql_usage = sql_usage.where(ApiUser.token == token)
    sql_usage = sql_usage.where(
        ApiUsage.timestamp >= datetime.utcnow() - timedelta(hours=1)
    )

    async with get_session(EngineType.PLAYERDATA) as session:
        api_user = await session.execute(sql)
        usage_data = await session.execute(sql_usage)

        api_user = sqlalchemy_result(api_user)
        usage_data = sqlalchemy_result(usage_data)

        api_user = api_user.rows2dict()
        usage_data = usage_data.rows2dict()

        # Checks to see if there is a user ID
        if not len(api_user) == 0:
            insert_values = {}
            insert_values["route"] = route
            insert_values["user_id"] = api_user[0]["id"]
            insert_usage = insert(ApiUsage).values(insert_values)
            await session.execute(insert_usage)
            await session.commit()

    # If len api_user == 0; user does not have necessary permissions
    if len(api_user) == 0:
        raise HTTPException(status_code=401, detail=f"Insufficent Permissions")

    api_user = api_user[0]

    if api_user["is_active"] != 1:
        raise HTTPException(status_code=403, detail=f"Insufficent Permissions")

    if (len(usage_data) > api_user["ratelimit"]) and (api_user["ratelimit"] != -1):
        raise HTTPException(status_code=429, detail=f"Your Ratelimit has been reached.")

    return True


async def batch_function(function, data, batch_size=100):
    """
    smaller transactions, can reduce locks, but individual transaction, can cause connection pool overflow
    """
    batches = []
    for i in range(0, len(data), batch_size):
        logger.debug({"batch": {f"{function.__name__}": f"{i}/{len(data)}"}})
        batch = data[i : i + batch_size]
        batches.append(batch)

    await asyncio.gather(*[create_task(function(batch)) for batch in batches])

    return
