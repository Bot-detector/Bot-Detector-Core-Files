from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import Label as dbLabel
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select, Select, Insert
from api.database.functions import PLAYERDATA_ENGINE
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import functions

router = APIRouter()


class label(BaseModel):
    label_name: str


@router.get("/v1/label/", tags=["Label"])
async def get_labels_from_plugin_database(token: str):
    """
    Selects all labels.
    """
    await verify_token(
        token, verification="request_highscores", route="[GET]/v1/label/"
    )

    sql:Select = select(dbLabel)

    data = await functions.retry_on_deadlock(sql, PLAYERDATA_ENGINE)
    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/label/", tags=["Label"])
async def insert_label_into_plugin_database(token: str, label: label):
    """
    Insert a new label & return the new label.
    """
    await verify_token(token, verification="verify_ban", route="[POST]/v1/label/")

    label_name = label.dict()
    label_name = label_name["label_name"]

    # insert query
    sql_insert:Insert = insert(dbLabel)
    sql_insert = sql_insert.values(label=label_name)
    sql_insert = sql_insert.prefix_with("ignore")

    # select query
    sql_select:Select = select(dbLabel)
    sql_select = sql_select.where(dbLabel.label == label_name)

    data = await functions.retry_on_deadlock(sql_insert, PLAYERDATA_ENGINE)
    data = await functions.retry_on_deadlock(sql_select, PLAYERDATA_ENGINE)
    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/v1/label/", tags=["Label"])
async def update_a_currently_existing_label(token: str):
    """
    Work in progress
    Update an existing label.
    """
    await verify_token(token, verification="verify_ban", route="[PUT]/v1/label/")
    return
