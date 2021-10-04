from inspect import isdatadescriptor
from typing import List, Optional
from database.functions import async_session, execute_sql, list_to_string, sql_cursor, sqlalchemy_result, verify_token, engine
from database.models import Player, PlayerHiscoreDataLatest
from database.models import Prediction as dbPrediction
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import delete, select, text
from sqlalchemy.sql.functions import func

router = APIRouter()


class Prediction(BaseModel):
    name: str
    Prediction: str
    id: int
    created: str
    Predicted_confidence: float
    Agility_Thieving_bot: float
    Agility_bot: float
    Construction_Magic_bot: float
    Construction_Prayer_bot: float
    Cooking_bot: float
    Crafting_bot: float
    Fishing_Cooking_bot: float
    Fishing_bot: float
    Fletching_bot: float
    Herblore_bot: float
    Hunter_bot: float
    Magic_bot: float
    Mining_bot: float
    PVM_Melee_bot: float
    PVM_Ranged_Magic_bot: float
    PVM_Ranged_bot: float
    Real_Player: float
    Runecrafting_bot: float
    Smithing_bot: float
    Thieving_bot: float
    Woodcutting_bot: float
    Zaff_BStaff_Bot: Optional[float] = 0
    Zalcano_bot: float
    mort_myre_fungus_bot: float

@router.get("/v1/prediction", tags=["prediction"])
async def get(token: str, name: str):
    '''
        select predictionf from database
    '''
    await verify_token(token, verifcation='hiscore')

    sql = select(dbPrediction)
    sql = sql.where(dbPrediction.name == name)
    
    async with async_session() as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()



@router.post("/v1/prediction", tags=["prediction"])
async def post(token: str, prediction: List[Prediction]):
    '''
        replace into prediction table
    '''
    await verify_token(token, verifcation='ban')

    data = [d.dict() for d in prediction]

    columns = list_to_string([k for k in data[0].keys()])
    values = list_to_string([f':{k}' for k in data[0].keys()])

    sql = f'''replace into Predictions ({columns}) values ({values})'''
    sql = text(sql)

    async with async_session() as session:
        await session.execute(sql, data)
        await session.commit()
    
    return {'ok':'ok'}

@router.get("/v1/prediction/data", tags=["prediction", "business-logic"])
async def get(token: str):
    '''
        GET: the hiscore data where prediction is not from today
    '''
    await verify_token(token, verifcation='hiscore')

    # query
    sql = select(columns=[PlayerHiscoreDataLatest, Player.name])
    sql = sql.where(func.date(dbPrediction.created) != func.curdate())
    sql = sql.order_by(func.rand())
    sql = sql.limit(50000).offset(0)
    sql = sql.join(Player).join(dbPrediction, isouter=True)

    async with async_session() as session:
        data = await session.execute(sql)
    
    names, objs, output = [], [], []
    for d in data:
        objs.append((d[0],))
        names.append(d[1])
    
    data = sqlalchemy_result(objs).rows2dict()

    for d, n in zip(data, names):
        d['name'] = n
        output.append(d)

    return output
