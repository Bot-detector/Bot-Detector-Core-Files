
from datetime import datetime, date
import logging
from typing import List, Optional

from api.database.functions import (EngineType, get_session,
                                    verify_token, sqlalchemy_result)
from api.database.models import Player, Prediction, Report, ReportLatest
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.sql.expression import insert, select
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


@router.get("/v1/report", tags=["Report"])
async def get_reports_from_plugin_database(
    token: str,
    reportedID: Optional[int]= Query(None, ge=0),
    reportingID: Optional[int]= Query(None, ge=0),
    timestamp: Optional[date]= None,
    regionID: Optional[int]= Query(None, ge=0, le=100000)
    ):
    '''
        Select report data.
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/report/')

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


@router.put("/v1/report", tags=["Report"])
async def update_reports(old_user_id: int, new_user_id: int, token: str):
    '''
        Update the reports from one reporting user to another.
    '''
    await verify_token(token, verification='verify_ban', route='[PUT]/v1/report/')
    # can be used for name change

    sql = update(Report)
    sql = sql.values(Report.reportingID == new_user_id)
    sql = sql.where(Report.reportingID == old_user_id)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql)

    return {'OK': 'OK'}


@router.post("/v1/report", tags=["Report"])
async def insert_report(token: str, detections: List[detection]):
    '''
        Work in progress 
        Insert report.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/report/')

    sql = insert(Report)
    pass

@router.get("/v1/report/prediction", tags=["Report", "Business"])
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
        Gets account based upon the prediction features.
        Business service: Twitter
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/report/prediction')
    
    
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

@router.get("/v1/report/latest", tags=["Report"])
async def get_latest_report_of_a_user(
    token: str,
    reported_id: int = Query(..., ge=0)
    ):
    
    '''
        Select the latest report data, by reported user
    '''
    
    await verify_token(token, verification='verify_ban', route='[GET]/v1/report/latest')

    sql = select(ReportLatest)

    if not reported_id is None:
        sql = sql.where(ReportLatest.reported_id == reported_id)
    
    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/v1/report/latest/bulk", tags=["Report"])
async def get_bulk_latest_report_data(
    token: str,
    region_id: Optional[int] = Query(None, ge=0, le=25000),
    timestamp: Optional[date] = None,
    count: Optional[bool] = True,
    ):
    '''
        get the player count in bulk by region and or date.
        Timestamp in the format of: YYYY-MM-DD
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/report/latest/bulk')

    sql = select(ReportLatest)

    if not timestamp is None:
        sql = sql.where(func.date(ReportLatest.timestamp) == timestamp)

    if not region_id is None:
        sql = sql.where(ReportLatest.region_id == region_id)

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    
    if count:
        now = datetime.utcnow()
        data = {'region_id': region_id,
                'count': len(data.rows2dict()),
                'timestamp': f'{now.hour}:{now.minute}:{now.second}'}
        return data
        
    return data.rows2dict()
