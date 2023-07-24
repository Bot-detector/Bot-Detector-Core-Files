import logging

from pydantic import ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.sql.expression import Delete, Insert, Select, Update, and_

from src.app.schemas.highscore import PlayerHiscoreData as SchemaPlayerHiscoreData
from src.app.schemas.player import Player as SchemaPlayer
from src.database.database import PLAYERDATA_ENGINE
from src.database.models import Player as dbPlayer
from src.database.models import playerHiscoreData as dbPlayerHiscoreData
from src.database.functions import handle_database_error

logger = logging.getLogger(__name__)


class PlayerHiscoreData:
    def __init__(self) -> None:
        pass

    @handle_database_error
    async def create(self, data: list[SchemaPlayerHiscoreData]):
        table = dbPlayerHiscoreData

        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session

            async with session.begin():
                insert_counter = 0
                for row in data:
                    # Create the insert statement
                    sql_insert: Insert = insert(table)
                    sql_insert = sql_insert.values(row.model_dump())

                    # Create the select statement to check if the record exists
                    sql_select: Select = select(table)
                    sql_select = sql_select.where(
                        and_(
                            dbPlayerHiscoreData.Player_id == row.Player_id,
                            dbPlayerHiscoreData.ts_date == row.ts_date,
                        )
                    )
                    # Execute the select query and check if the record exists
                    result: AsyncResult = await session.execute(sql_select)
                    existing_record = result.scalars().all()

                    if not existing_record:
                        # If the record does not exist, insert it
                        await session.execute(sql_insert)
                        insert_counter += 1

        logger.info(f"Received: {len(data)}, inserted: {insert_counter}")
        return

    @handle_database_error
    async def read(self, player_name: str, page: int = 1, page_size: int = 10):
        table = dbPlayerHiscoreData

        sql_select: Select = select(table)
        sql_select = sql_select.join(
            target=dbPlayer, onclause=dbPlayerHiscoreData.Player_id == dbPlayer.id
        )
        sql_select = sql_select.where(dbPlayer.name == player_name)
        sql_select = sql_select.order_by(dbPlayerHiscoreData.id.desc())
        sql_select = sql_select.limit(page_size).offset((page - 1) * page_size)

        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            # Execute the select query
            result: AsyncResult = await session.execute(sql_select)

        # Convert the query results to SchemaPlayerHiscoreData objects
        schema_data = []
        for row in result.scalars().all():
            try:
                schema_data.append(SchemaPlayerHiscoreData.model_validate(row))
            except ValidationError as e:
                print(e)
        return schema_data

    @handle_database_error
    async def update(self, data: SchemaPlayerHiscoreData):
        pass

    @handle_database_error
    async def delete(self, player_name: str):
        pass
