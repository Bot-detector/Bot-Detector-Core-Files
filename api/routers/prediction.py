from operator import or_
from typing import List, Optional

from api.database.database import EngineType, get_session
from api.database.functions import (list_to_string, sqlalchemy_result,
                                    verify_token)
from api.database.models import Player, PlayerHiscoreDataLatest
from api.database.models import Prediction as dbPrediction
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql.expression import select, text
from sqlalchemy.sql.functions import func

router = APIRouter()


class Prediction(BaseModel):
    name: str
    Prediction: str
    id: int
    created: str
    Predicted_confidence: float
    Real_Player: Optional[float] = 0
    PVM_Melee_bot: Optional[float] = 0
    Smithing_bot: Optional[float] = 0
    Magic_bot: Optional[float] = 0
    Fishing_bot: Optional[float] = 0
    Mining_bot: Optional[float] = 0
    Crafting_bot: Optional[float] = 0
    PVM_Ranged_Magic_bot: Optional[float] = 0
    PVM_Ranged_bot: Optional[float] = 0
    Hunter_bot: Optional[float] = 0
    Fletching_bot: Optional[float] = 0
    Clue_Scroll_bot: Optional[float] = 0
    LMS_bot: Optional[float] = 0
    Agility_bot: Optional[float] = 0
    Wintertodt_bot: Optional[float] = 0
    Runecrafting_bot: Optional[float] = 0
    Zalcano_bot: Optional[float] = 0
    Woodcutting_bot: Optional[float] = 0
    Thieving_bot: Optional[float] = 0
    Soul_Wars_bot: Optional[float] = 0
    Cooking_bot: Optional[float] = 0
    Vorkath_bot: Optional[float] = 0
    Barrows_bot: Optional[float] = 0
    Herblore_bot: Optional[float] = 0


@router.get("/v1/prediction", tags=["prediction"])
async def get(token: str, name: str):
    '''
        select predictionf from database
    '''
    await verify_token(token, verifcation='hiscore')

    sql = select(dbPrediction)
    sql = sql.where(dbPrediction.name == name)
    
    async with get_session(EngineType.PLAYERDATA) as session:
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

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql, data)
        await session.commit()
    
    return {'ok':'ok'}

@router.get("/v1/prediction/data", tags=["prediction", "business-logic"])
async def get(token: str, limit: int = 50_000):
    '''
        GET: the hiscore data where prediction is not from today
    '''
    await verify_token(token, verifcation='hiscore')

    # query
    sql = select(columns=[PlayerHiscoreDataLatest, Player.name])
    sql = sql.where(
        or_(
            func.date(dbPrediction.created) != func.curdate(),
            dbPrediction.created == None
        )
    )
    sql = sql.order_by(func.rand())
    sql = sql.limit(limit).offset(0)
    sql = sql.join(Player).join(dbPrediction, isouter=True)
    
    async with get_session(EngineType.PLAYERDATA) as session:
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
