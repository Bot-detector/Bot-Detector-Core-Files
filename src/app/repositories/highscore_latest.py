import logging

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
from src.database.database import PLAYERDATA_ENGINE
from src.database.functions import handle_database_error
from src.database.models import Player as dbPlayer
from src.database.models import PlayerHiscoreDataLatest as dbPlayerHiscoreDataLatest

logger = logging.getLogger(__name__)


class PlayerHiscoreDataLatest:
    def __init__(self):
        pass

    @handle_database_error
    async def read(
        self, gte_player_id: int = None, page: int = None, page_size: int = None
    ):
        table = dbPlayerHiscoreDataLatest

        sql_select = select(table)
        sql_select = sql_select.join(
            target=dbPlayer, onclause=table.Player_id == dbPlayer.id
        )
        sql_select = sql_select.order_by(table.Player_id.asc())

        if gte_player_id:
            sql_select = sql_select.where(table.Player_id >= gte_player_id)

        if page_size:
            sql_select = sql_select.limit(page_size)

        if page is not None and page_size:
            sql_select = sql_select.offset((page - 1) * page_size)

        async with PLAYERDATA_ENGINE.get_session() as session:
            session: AsyncSession
            # Execute the select query
            result = await session.execute(sql_select)

        # Convert the query results to SchemaHiscore objects
        schema_data = []
        for row in result.scalars().all():
            try:
                row_dict: dict = jsonable_encoder(row)
                row_dict = {k: v if v is not None else 0 for k, v in row_dict.items()}
                model_row = SchemaHiscore.model_validate(row_dict)
                schema_data.append(model_row)
            except Exception as e:
                logger.error({"error": str(e), "data": row_dict})

        return schema_data
