
from datetime import datetime, date
import logging
from typing import List, Optional

from sqlalchemy.sql.selectable import FromClause

from api.database.functions import (EngineType, get_session, sql_cursor,
                                    verify_token, sqlalchemy_result)
from api.database.models import Player, Prediction, Report
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.sql.expression import insert, select
from sqlalchemy import Date
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)
router = APIRouter()


class equipment(BaseModel):
    equip_head_id: int
    equip_amulet_id: int
    equip_torso_id: int
    equip_legs_id: int
    equip_boots_id: int
    equip_cape_id: int
    equip_hands_id: int
    equip_weapon_id: int
    equip_shield_id: int


class detection(BaseModel):
    reportedID: int
    reportingID: int
    region_id: int
    x_coord: int
    y_coord: int
    z_coord: int
    ts: int
    manual_detect: int
    on_members_world: int
    on_pvp_world: int
    world_number: int
    equipment: equipment
    equip_ge_value: int


@router.get("/v1/report", tags=["report"])
async def get_reports(
    token: str,
    reportedID: Optional[int]=None,
    reportingID: Optional[int]=None,
    timestamp: Optional[date]=None,
    regionID: Optional[int]=None
    ):
    '''
        Selects report data from the plugin database for an account.
    '''
    await verify_token(token, verifcation='hiscore')

    if None == reportedID == reportingID:
        raise HTTPException(status_code=404, detail="reportedID or reportingID must be given")

    sql = select(Report)

    if not reportedID is None:
        sql = sql.where(Report.reportedID == reportedID)

    if not reportingID is None:
        sql = sql.where(Report.reportingID == reportingID)

    if not timestamp is None:
        sql = sql.where(func.date(Report.timestamp) == timestamp)

    if not regionID is None:
        sql = sql.where(Report.region_id == regionID)
    
    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/v1/report", tags=["report"])
async def update_report(old_user_id: int, new_user_id: int, token: str):
    '''
        Updates a user's new user ID from an old user ID. This can be used to transfer report data from one RSN to another RSN.
    '''
    await verify_token(token, verifcation='ban')
    # can be used for name change

    sql = update(Report)
    sql = sql.values(Report.reportingID == new_user_id)
    sql = sql.where(Report.reportingID == old_user_id)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql)

    return {'OK': 'OK'}


@router.post("/v1/report", tags=["report"])
async def insert_report(token: str, detections: List[detection]):
    '''
        Inserts report data from the Bot Detector Plugin into the database. 
    '''
    await verify_token(token, verifcation='ban')

    sql = insert(Report)
    pass

@router.get("/v1/report/prediction", tags=["report"])
async def get_report_by_prediction(
    token: str,
    label_jagex: int,
    predicted_confidence: int,
    prediction: Optional[str]=None,
    real_player: Optional[int]=None,
    crafting_bot: Optional[int]=None,
    timestamp: Optional[date]=None,
    region_id: Optional[int]=None
    ):
    '''
        Gets account based upon the prediction, confidence, and region id.
    '''
    await verify_token(token, verifcation='ban')
    
    
    sql = select(   
        Player.id, 
        Prediction.Prediction, 
        Prediction.Predicted_confidence
    ).distinct()

    sql = sql.where(Prediction.Predicted_confidence >= predicted_confidence)
    sql = sql.where(Player.label_jagex == label_jagex)

    if not prediction is None:
        sql = sql.where(Prediction.Prediction == prediction)

    if not real_player is None:
        sql = sql.where(Prediction.Real_Player < real_player)

    if not crafting_bot is None:
        sql = sql.where(Prediction.Crafting_bot > crafting_bot)

    if not timestamp is None:
        sql = sql.where(func.date(Report.timestamp) == timestamp)
    
    if not region_id is None:
        sql = sql.where(Report.region_id == region_id)
    
    sql = sql.join(Report, Player.id == Report.reportedID)
    sql = sql.join(Prediction, Player.id == Prediction.id)

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    output = []
    for row in data:
        mydata = {}
        mydata['id'] = row[0]
        mydata['prediction'] = row[1]
        mydata['Predicted_confidence'] = row[2]
        output.append(mydata)

    return output