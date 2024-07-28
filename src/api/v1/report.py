import logging
from datetime import date
from typing import List, Optional
import asyncio
from src.database import functions
from src.database.functions import PLAYERDATA_ENGINE
from src.database.models import (
    Player,
    Report,
)
from src.utils import logging_helpers
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Select, select, update
import aiohttp
import traceback

logger = logging.getLogger(__name__)
router = APIRouter()

upper_gear_cost = 1_000_000_000_000

# TODO: cleanup thse functions
class equipment(BaseModel):
    equip_head_id: int = Field(0, ge=0)
    equip_amulet_id: int = Field(0, ge=0)
    equip_torso_id: int = Field(0, ge=0)
    equip_legs_id: int = Field(0, ge=0)
    equip_boots_id: int = Field(0, ge=0)
    equip_cape_id: int = Field(0, ge=0)
    equip_hands_id: int = Field(0, ge=0)
    equip_weapon_id: int = Field(0, ge=0)
    equip_shield_id: int = Field(0, ge=0)


class detection(BaseModel):
    reporter: str = Field(..., min_length=1, max_length=13)
    reported: str = Field(..., min_length=1, max_length=12)
    region_id: int = Field(0, ge=0, le=100_000)
    x_coord: int = Field(0, ge=0)
    y_coord: int = Field(0, ge=0)
    z_coord: int = Field(0, ge=0)
    ts: int = Field(0, ge=0)
    manual_detect: int = Field(0, ge=0, le=1)
    on_members_world: int = Field(0, ge=0, le=1)
    on_pvp_world: int = Field(0, ge=0, le=1)
    world_number: int = Field(0, ge=300, le=1_000)
    equipment: equipment
    equip_ge_value: int = Field(0, ge=0, le=int(upper_gear_cost))


@router.get("/report", tags=["Report"])
async def get_reports(
    token: str,
    request: Request,
    reportedID: Optional[int] = Query(None, ge=0),
    reportingID: Optional[int] = Query(None, ge=0),
    timestamp: Optional[date] = None,
    regionID: Optional[int] = Query(None, ge=0, le=100000),
):
    """
    Select report data.
    """
    await functions.verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    if None == reportedID == reportingID:
        raise HTTPException(
            status_code=404, detail="reportedID or reportingID must be given"
        )

    sql = select(Report)

    if reportedID is not None:
        sql = sql.where(Report.reportedID == reportedID)

    if reportingID is not None:
        sql = sql.where(Report.reportingID == reportingID)

    if timestamp is not None:
        sql = sql.where(func.date(Report.timestamp) == timestamp)

    if regionID is not None:
        sql = sql.where(Report.region_id == regionID)

    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = functions.sqlalchemy_result(data)
    return data.rows2dict()

@router.put("/report", tags=["Report"])
async def update_reports(
    old_user_id: int, new_user_id: int, token: str, request: Request
):
    """
    Update the reports from one reporting user to another.
    """
    await functions.verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )
    # can be used for name change

    sql = update(Report)
    sql = sql.values(reportingID=new_user_id)
    sql = sql.where(Report.reportingID == old_user_id)
    sql = sql.prefix_with("ignore")

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"detail": f"{data.rowcount} rows updated to reportingID = {new_user_id}."}

async def insert_report_v2(detections: list[detection]):
    url = 'http://public-api-svc.bd-prd.svc:5000/v2/report'
    try:
        data = [d.dict() for d in detections]
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as response:
                if not response.ok:
                    response_text = await response.text()
                    logger.warning(f"Request to {url} failed with status {response.status} and response: {response_text}")
    except aiohttp.ClientError as e:
        # Log client-specific errors with request details
        logger.error(f"Client error during request to {url} with payload {data}: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        # Log general exceptions with traceback
        logger.error(f"Unexpected error during request to {url} with payload {data}: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")

@router.post("/report", status_code=status.HTTP_201_CREATED, tags=["Report"])
async def insert_report(
    detections: List[detection],
    manual_detect: int = Query(None, ge=0, le=1),
):
    """
    Inserts detections into to the plugin database.
    """
    asyncio.create_task(insert_report_v2(detections))
    return {"detail": "ok"}

async def select_report_count_v1(name:str, manual_detect:int):
    name = await functions.to_jagex_name(name)

    voter: Player = aliased(Player, name="voter")
    subject: Player = aliased(Player, name="subject")

    sub_query: Select = select(Report.reportedID.distinct().label("reportedID"))
    sub_query = sub_query.join(voter, Report.reportingID == voter.id)
    sub_query = sub_query.where(voter.name == name)
    sub_query = sub_query.where(Report.manual_detect == manual_detect)

    # Create an alias for the subquery
    sub_query_alias = sub_query.alias("DistinctReports")

    sql: Select = select(
        func.count(subject.id),
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player,
    )
    sql = sql.select_from(sub_query_alias)
    sql = sql.join(
        subject, sub_query_alias.c.reportedID == subject.id
    )  # Use c to access columns
    sql = sql.group_by(
        subject.confirmed_ban, subject.possible_ban, subject.confirmed_player
    )

    keys = ["count", "confirmed_ban", "possible_ban", "confirmed_player"]
    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)
            data = [{k: v for k, v in zip(keys, d)} for d in data]
    return data

@router.get("/report/count", tags=["Report"])
async def get_report_count_v1(name: str):
    """
    """
    data = await select_report_count_v1(name=name, manual_detect=0)
    return data

@router.get("/report/manual/count", tags=["Report"])
async def get_report_manual_count_v1(name: str):
    """
    Get the calculated player report count
    """
    data = await select_report_count_v1(name=name, manual_detect=1)
    return data