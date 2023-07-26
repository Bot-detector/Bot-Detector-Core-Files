import logging
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Delete, Insert, Select, Update, and_

from src.app.schemas.stg_report import StgReport as SchemaStgReport
from src.database.database import PLAYERDATA_ENGINE
from src.database.functions import handle_database_error
from src.database.models import stgReport as dbstgReport

logger = logging.getLogger(__name__)


class stgReport:
    def __init__(self) -> None:
        pass

    @handle_database_error
    async def create(self, data: list[SchemaStgReport]):
        table = dbstgReport
        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session

            async with session.begin():
                for row in data:
                    # Create the insert statement
                    sql_insert: Insert = insert(table)
                    sql_insert = sql_insert.values(row.model_dump())

        logger.info(f"inserted: {len(data)}")
        return
