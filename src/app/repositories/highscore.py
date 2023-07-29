import logging

from pydantic import ValidationError
from sqlalchemy import delete, insert, select, update, union_all
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.sql.expression import Delete, Insert, Select, Update, and_

from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
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
    async def _get_unique(self, data: list[SchemaHiscore]) -> list[SchemaHiscore]:
        table = dbPlayerHiscoreData

        # Create a list of queries to be used in the UNION operation.
        select_queries = []
        for row in data:
            # Define the condition to match the row's Player_id and ts_date with the database records.
            condition = and_(
                dbPlayerHiscoreData.Player_id == row.Player_id,
                dbPlayerHiscoreData.ts_date == row.timestamp.date(),
            )
            # Append the SELECT query with the condition to the list.
            select_queries.append(select(table).where(condition))

        # Perform a UNION of all the SELECT queries to combine the results.
        final_query = union_all(*select_queries)

        # Get an async session from the PLAYERDATA_ENGINE.
        async with PLAYERDATA_ENGINE.get_session() as session:
            # Cast the session to AsyncSession for type hinting.
            session: AsyncSession = session

            # Execute the final_query and fetch the results.
            result: AsyncResult = await session.execute(final_query)
            # Extract all the results from the query.
            result = result.all()

        # Return the list of results obtained from the database.
        return result

    @handle_database_error
    async def create(self, data: list[SchemaHiscore]) -> list[SchemaHiscore]:
        # Define the table to work with
        table = dbPlayerHiscoreData

        existing_record = await self._get_unique(data)
        unique = [f"{r.ts_date}-{r.Player_id}" for r in existing_record]

        values: list[SchemaHiscore] = []

        for row in data:
            key = f"{row.timestamp.date()}-{row.Player_id}"
            if key in unique:
                continue
            values.append(row)

        if not values:
            logger.info(f"Received: {len(data)}, inserted: {len(values)}")
            return values

        # Get a session from the PLAYERDATA_ENGINE to perform the database operations
        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                sql_insert: Insert = insert(table)
                sql_insert = sql_insert.values([v.model_dump() for v in values])
                sql_insert = sql_insert.prefix_with("ignore")

                # Execute the insert statement within the session
                await session.execute(sql_insert)

        # Log the number of received and inserted data rows and return the rows that were inserted
        logger.info(f"Received: {len(data)}, inserted: {len(values)}")
        return values

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

        # Convert the query results to SchemaHiscore objects
        schema_data = []
        for row in result.scalars().all():
            try:
                schema_data.append(SchemaHiscore.model_validate(row))
            except ValidationError as e:
                print(e)
        return schema_data

    @handle_database_error
    async def update(self, data: SchemaHiscore):
        pass

    @handle_database_error
    async def delete(self, player_name: str):
        pass
