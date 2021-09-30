from database.database import async_session
from database.functions import sqlalchemy_result, verify_token
from database.models import Label as dbLabel
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select

router = APIRouter()

class label(BaseModel):
    label_name:str

@router.get("/v1/label/", tags=["label"])
async def get(token:str):
    '''
        select a label from db
    '''
    await verify_token(token, verifcation='hiscore')

    sql = select(dbLabel)

    async with async_session() as session:
        data = await session.execute(sql)
    
    data = sqlalchemy_result(data)
    return data.rows2dict()
    


@router.post("/v1/label/", tags=["label"])
async def post(token:str, label:label):
    '''
        insert a label into the db
    '''
    await verify_token(token, verifcation='ban')

    label_name = label.dict()
    label_name = label_name['label_name']

    # insert query
    sql_insert = insert(dbLabel)
    sql_insert = sql_insert.values(label=label_name)
    sql_insert = sql_insert.prefix_with('ignore')

    # select query
    sql_select = select(dbLabel)
    sql_select = sql_select.where(dbLabel.label == label_name)

    async with async_session() as session:
        await session.execute(sql_insert)
        await session.commit()
        data = await session.execute(sql_select)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.put("/v1/label/", tags=["label"])
async def put(token:str):
    '''
        update a label into the datase
    '''
    await verify_token(token, verifcation='ban')
    return
