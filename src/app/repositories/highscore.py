import logging

from pydantic import BaseModel, ValidationError
from sqlalchemy import select, union_all
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.sql.expression import Insert, Select, and_

from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
from src.database.database import PLAYERDATA_ENGINE
from src.database.functions import handle_database_error
from src.database.models import Player as dbPlayer
from src.database.models import playerHiscoreData as dbPlayerHiscoreData

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
            session: AsyncSession

            # Execute the final_query and fetch the results.
            result: AsyncResult = await session.execute(final_query)
            # Extract all the results from the query.
            result = result.all()

        # Return the list of results obtained from the database.
        return result

    @handle_database_error
    async def insert_if_not_exist(
        self,
        table,
        schema: BaseModel,
        unique_columns: list[str],
        values: list[BaseModel],
    ):
        # Convert values into a dictionary of unique records based on unique_columns
        unique_records = {
            "-".join([str(getattr(v, c)) for c in unique_columns]): v for v in values
        }

        # Create a list of SQL queries to check for existing rows with unique values
        queries = []
        for v in unique_records.values():
            sql_select: Select = select(table)
            for c in unique_columns:
                value = getattr(v, c)
                column = getattr(table, c)
                sql_select = sql_select.where(column == value)
            queries.append(sql_select)

        # Union all the queries to combine the results
        final_query = union_all(*queries)

        # Open a database session and begin a transaction
        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                # Execute the final query to check for existing rows
                existing_rows = await session.execute(final_query)
                existing_rows = existing_rows.all()

                # If existing rows are found, remove them from unique_records dictionary
                if existing_rows:
                    for row in existing_rows:
                        row = schema.model_validate(row)
                        unique_row = "-".join(
                            [str(getattr(row, c)) for c in unique_columns]
                        )
                        unique_records.pop(unique_row, None)

                # If there are remaining unique records, insert them into the database
                if unique_records:
                    # Create an insert statement with the unique records
                    sql_insert: Insert = insert(table)
                    sql_insert = sql_insert.values(
                        [v.model_dump() for v in unique_records.values()]
                    )
                    sql_insert = sql_insert.prefix_with("ignore")

                    # Execute the insert statement within the session
                    await session.execute(sql_insert)

        # Log the number of queries and inserted records
        logger.info(f"Received: {len(queries)}, inserted: {len(unique_records)}")
        return

    @handle_database_error
    async def create(self, data: list[SchemaHiscore]) -> list[SchemaHiscore]:
        # Define the table to work with
        table = dbPlayerHiscoreData

        # Get a session from the PLAYERDATA_ENGINE to perform the database operations
        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                sql_insert: Insert = insert(table)
                sql_insert = sql_insert.values([d.model_dump() for d in data])
                sql_insert = sql_insert.prefix_with("ignore")

                # Execute the insert statement within the session
                await session.execute(sql_insert)

        # Log the number of received and inserted data rows and return the rows that were inserted
        logger.info(f"Received: {len(data)}, inserted: {len(data)}")
        return data

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
