import asyncio
import logging
import random
import re
import traceback
from asyncio.tasks import create_task
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy import Text, text
from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.sql.expression import insert, select

# Although never directly used, the engines are imported to add a permanent reference
# to these entities to prevent the
# garbage collector from trying to dispose of our engines.
from src.database.database import PLAYERDATA_ENGINE, Engine, EngineType
from src.database.models import ApiPermission, ApiUsage, ApiUser, ApiUserPerm

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


async def parse_sql(
    sql, param: dict, has_return: bool, row_count: int, page: int
) -> tuple[Text, bool]:
    if isinstance(sql, Text):
        return sql
    elif isinstance(sql, str):
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
        sql: Text = text(sql)
    return sql, has_return


async def execute_sql(
    sql,
    param: dict = {},
    debug: bool = False,
    engine: Engine = PLAYERDATA_ENGINE,
    row_count: int = 100_000,
    page: int = 1,
    has_return: bool = None,
    retry_attempt: int = 0,
):
    # retry breakout
    if retry_attempt >= 5:
        logger.debug({"message": "Too many retries"})
        return None

    sleep = retry_attempt * 5
    sql, has_return = await parse_sql(sql, param, has_return, row_count, page)

    try:
        async with engine.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                rows = await session.execute(sql, param)
                records = sql_cursor(rows) if has_return else None
    # OperationalError = Deadlock, InternalError = lock timeout
    except Exception as e:
        if isinstance(e, InternalError):
            e = e if debug else ""
            logger.debug(
                {"message": f"Lock, Retry Attempt: {retry_attempt}, retrying: {e}"}
            )
        elif isinstance(e, OperationalError):
            e = e if debug else ""
            logger.debug(
                {"message": f"Deadlock, Retry Attempt: {retry_attempt}, retrying {e}"}
            )
        else:
            err = {"message": "Unknown Error", "error": e}
            logger.error(f"{err}\n{traceback.format_exc()}")
            return None
        await asyncio.sleep(random.uniform(0.1, sleep))
        records = await execute_sql(
            sql,
            param,
            debug,
            engine,
            row_count,
            page,
            has_return=has_return,
            retry_attempt=retry_attempt + 1,
        )
    return records


class sql_cursor:
    def __init__(self, rows):
        self.rows: AsyncResult = rows

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

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
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


def handle_database_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except OperationalError as e:
            # Handle the OperationalError here (you can log the error, retry, etc.)
            # {traceback.format_exc()}
            logger.error(f"Caught OperationalError:\n{e}\n{traceback.format_exc()}")
            # Add a random sleep time between 100ms to 1000ms (adjust as needed).
            sleep_time_ms = random.randint(100, 2000)
            await asyncio.sleep(sleep_time_ms / 1000)
            # Retry the operation by calling the wrapper again (could be recursive).
            return await wrapper(*args, **kwargs)

    return wrapper
