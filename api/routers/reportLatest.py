
import logging
from datetime import date, datetime
from typing import List, Optional
import time

from api.database.functions import (EngineType, get_session, sql_cursor,
                                    sqlalchemy_result, verify_token)
from api.database.models import Player, Prediction, ReportLatest
from api.routers.legacy import RegionID
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Date, update
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import insert, select
from sqlalchemy.sql.functions import count
from sqlalchemy.sql.selectable import FromClause

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


@router.get("/v1/reportLatest", tags=["Report Latest"])
async def get_reportLatest_from_plugin_database(
    token: str,
    reported_id: Optional[int]= Query(None, ge=0),
    timestamp: Optional[date]= None,
    regionID: Optional[int]= Query(None, ge=0, le=100000)
    ):
    
    '''
        Select the latest report data.
    '''
    
    await verify_token(token, verification='verify_ban', route='[GET]/v1/reportLatest')

    if None == reported_id:
        raise HTTPException(status_code=404, detail="reportedID or reportingID must be given")

    sql = select(ReportLatest)

    if not reported_id is None:
        sql = sql.where(ReportLatest.reported_id == reported_id)
    if not timestamp is None:
        sql = sql.where(func.date(ReportLatest.timestamp) == timestamp)
    if not regionID is None:
        sql = sql.where(ReportLatest.region_id == regionID)
    
    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/reportLatest/daily-player-count", tags=["Report Latest"])
async def get_daily_player_count(
    token: str,
    regionID: Optional[int]= Query(None, ge=0, le=100000)
    ):
    """
        Get in-game player count for the day. This route resets at 0 UTC.
    """
    
    await verify_token(token, verification='verify_ban', route='[GET]/v1/reportLatest/daily-player-count')
    
    sql = select(ReportLatest)
    if not regionID is None:
        sql = sql.filter(ReportLatest.region_id == regionID)
    sql = sql.where(func.date(ReportLatest.timestamp)==func.current_date())
    
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    
    now = datetime.utcnow()
    current_time = f'{now.hour}:{now.minute}:{now.second}'
    
    response = {
                'players':len(data.rows2dict()),
                'regionID':regionID,
                'time':current_time
                }
    return response
