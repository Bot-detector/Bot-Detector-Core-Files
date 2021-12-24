from api.database.database import EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import Label as dbLabel
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select

router = APIRouter()

class label(BaseModel):
    label_name:str

@router.get("/v1/label/", tags=["label"])
async def get(token:str):
    '''
        Selects a label from the plugin database. 
    '''
    await verify_token(token, verification='request_highscores', route='[GET]/v1/label/')

    sql = select(dbLabel)

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)
    
    data = sqlalchemy_result(data)
    return data.rows2dict()
    
@router.post("/v1/label/", tags=["label"])
async def post(token:str, label:label):
    '''
        Creates a new label, and inserts it into the database.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/label/')

    label_name = label.dict()
    label_name = label_name['label_name']

    # insert query
    sql_insert = insert(dbLabel)
    sql_insert = sql_insert.values(label=label_name)
    sql_insert = sql_insert.prefix_with('ignore')

    # select query
    sql_select = select(dbLabel)
    sql_select = sql_select.where(dbLabel.label == label_name)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.put("/v1/label/", tags=["label"])
async def put(token:str):
    '''
        Updates an existing label in the database.
    '''
    await verify_token(token, verification='verify_ban', route='[PUT]/v1/label/')
    return
