import logging

from pydantic import ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.sql.expression import Delete, Insert, Select, Update, and_

from src.app.schemas.player import Player as SchemaPlayer
from src.database.database import PLAYERDATA_ENGINE
from src.database.functions import handle_database_error
from src.database.models import Player as dbPlayer

logger = logging.getLogger(__name__)


class Player:
    def __init__(self) -> None:
        pass

    @handle_database_error
    async def create(self, data: list[SchemaPlayer]):
        table = dbPlayer
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
                    sql_select = sql_select.where(dbPlayer.id == row.id)
                    # Execute the select query and check if the record exists
                    result: AsyncResult = await session.execute(sql_select)
                    existing_record = result.scalars()

                    if not existing_record:
                        # If the record does not exist, insert it
                        await session.execute(sql_insert)
                        insert_counter += 1

        logger.info(f"Received: {len(data)}, inserted: {insert_counter}")
        return

    @handle_database_error
    async def read(self, player_name: str, page: int = 1, page_size: int = 10):
        table = dbPlayer

        sql_select: Select = select(table)

        sql_select = sql_select.where(dbPlayer.name == player_name)
        sql_select = sql_select.limit(page_size).offset((page - 1) * page_size)

        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            # Execute the select query
            result: AsyncResult = await session.execute(sql_select)

        # Convert the query results to SchemaPlayerHiscoreData objects
        schema_data = []
        for row in result.scalars().all():
            try:
                schema_data.append(SchemaPlayer.model_validate(row))
            except ValidationError as e:
                print(e)
        return schema_data

    @handle_database_error
    async def update(self, data: list[SchemaPlayer]):
        # Select the database table to update.
        table = dbPlayer

        # check if we got some data
        if not data:
            logger.info(f"Updated {len(data)}")
            return

        # Get an asynchronous session from the PLAYERDATA_ENGINE.
        async with PLAYERDATA_ENGINE.get_session() as session:
            # Cast the session as an AsyncSession for type hinting.
            session: AsyncSession = session

            # Start a transaction within the session.
            async with session.begin():
                # Iterate through the data list to update each row.
                for row in data:
                    # Prepare the SQL UPDATE statement for the specific row using the row's ID.
                    sql_update: Update = update(table).where(dbPlayer.id == row.id)
                    sql_update = sql_update.values(
                        updated_at=row.updated_at,
                        possible_ban=row.possible_ban,
                        confirmed_ban=row.confirmed_ban,
                        confirmed_player=row.confirmed_player,
                        label_id=row.label_id,
                        label_jagex=row.label_jagex,
                    )

                    # Execute the UPDATE statement within the session.
                    await session.execute(sql_update)

        # Log the number of rows updated.
        logger.info(f"Updated {len(data)}")

        # Return from the function.
        return

    @handle_database_error
    async def delete(self, player_name: str):
        pass

    @handle_database_error
    async def read_many(
        self, page: int = None, page_size: int = 10_000, greater_than: int = None
    ):
        table = dbPlayer

        sql_select: Select = select(table)

        if greater_than:
            sql_select = sql_select.where(table.id > greater_than).limit(page_size)

        if page:
            sql_select = sql_select.limit(page_size).offset((page - 1) * page_size)

        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession
            # Execute the select query
            result: AsyncResult = await session.execute(sql_select)

        # Convert the query results to SchemaPlayerHiscoreData objects
        schema_data = []
        for row in result.scalars().all():
            try:
                schema_data.append(SchemaPlayer.model_validate(row))
            except ValidationError as e:
                logger.error(e)
        return schema_data
