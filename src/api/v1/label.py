from src.database.database import EngineType
from src.database.functions import sqlalchemy_result, verify_token
from src.database.models import Label as dbLabel
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select
from src.database.functions import PLAYERDATA_ENGINE
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class label(BaseModel):
    label_name: str


@router.get("/label/", tags=["Label"])
async def get_labels_from_plugin_database(token: str):
    """
    Selects all labels.
    """
    await verify_token(
        token, verification="request_highscores", route="[GET]/v1/label/"
    )

    sql = select(dbLabel)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/label/", tags=["Label"])
async def insert_label_into_plugin_database(token: str, label: label):
    """
    Insert a new label & return the new label.
    """
    await verify_token(token, verification="verify_ban", route="[POST]/v1/label/")

    label_name = label.dict()
    label_name = label_name["label_name"]

    # insert query
    sql_insert = insert(dbLabel)
    sql_insert = sql_insert.values(label=label_name)
    sql_insert = sql_insert.prefix_with("ignore")

    # select query
    sql_select = select(dbLabel)
    sql_select = sql_select.where(dbLabel.label == label_name)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql_insert)
        async with session.begin():
            data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/label/", tags=["Label"])
async def update_a_currently_existing_label(token: str):
    """
    Work in progress
    Update an existing label.
    """
    await verify_token(token, verification="verify_ban", route="[PUT]/v1/label/")
    return
