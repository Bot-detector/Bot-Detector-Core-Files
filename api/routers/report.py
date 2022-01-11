
import logging
import time
from datetime import date
from typing import List, Optional

import pandas as pd
from pydantic.fields import Field
from api.database.functions import (EngineType, batch_function, get_session,
                                    jagexify_names_list, sqlalchemy_result,
                                    to_jagex_name, verify_token)
from api.database.models import (Player, Prediction, Report, ReportLatest,
                                 stgReport)
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import insert, select

logger = logging.getLogger(__name__)
router = APIRouter()

# TODO: put these in the correct place
report_maximum = 5000
front_time_buffer = 3600
back_time_buffer = 25200
upper_gear_cost = 1_000_000_000_000

# TODO: cleanup thse functions


async def sql_select_players(names: List[str]) -> List:
    sql = select(Player)
    sql = sql.where(Player.normalized_name.in_(tuple(await jagexify_names_list(names))))
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)
    data = sqlalchemy_result(data)
    return [] if not data else data.rows2dict()


async def sql_insert_player(new_names: List[dict]) -> None:
    sql = insert(Player)
    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql, new_names)
        await session.commit()


async def sql_insert_report(param: dict) -> None:
    sql = insert(stgReport)
    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql, param)
        await session.commit()


async def parse_detection(data: dict) -> dict:
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    equipment = data.get('equipment', {})

    param = {
        'reportedID': data.get('id'),
        'reportingID': data.get('reporter_id'),
        'region_id': data.get('region_id'),
        'x_coord': data.get('x_coord'),
        'y_coord': data.get('y_coord'),
        'z_coord': data.get('z_coord'),
        'timestamp': human_time,
        'manual_detect': data.get('manual_detect'),
        'on_members_world': data.get('on_members_world'),
        'on_pvp_world': data.get('on_pvp_world'),
        'world_number': data.get('world_number'),
        'equip_head_id': equipment.get('equip_head_id'),
        'equip_amulet_id': equipment.get('equip_amulet_id'),
        'equip_torso_id': equipment.get('equip_torso_id'),
        'equip_legs_id': equipment.get('equip_legs_id'),
        'equip_boots_id': equipment.get('equip_boots_id'),
        'equip_cape_id': equipment.get('equip_cape_id'),
        'equip_hands_id': equipment.get('equip_hands_id'),
        'equip_weapon_id': equipment.get('equip_weapon_id'),
        'equip_shield_id': equipment.get('equip_shield_id'),
        'equip_ge_value': data.get('equip_ge_value', 0)
    }
    return param


class equipment(BaseModel):
    equip_head_id: int = Field(None, ge=0)
    equip_amulet_id: int = Field(None, ge=0)
    equip_torso_id: int = Field(None, ge=0)
    equip_legs_id: int = Field(None, ge=0)
    equip_boots_id: int = Field(None, ge=0)
    equip_cape_id: int = Field(None, ge=0)
    equip_hands_id: int = Field(None, ge=0)
    equip_weapon_id: int = Field(None, ge=0)
    equip_shield_id: int = Field(None, ge=0)


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


@router.get("/v1/report", tags=["Report"])
async def get_reports_from_plugin_database(
    token: str,
    reportedID: Optional[int] = Query(None, ge=0),
    reportingID: Optional[int] = Query(None, ge=0),
    timestamp: Optional[date] = None,
    regionID: Optional[int] = Query(None, ge=0, le=100000)
):
    '''
        Select report data.
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/report/')

    if None == reportedID == reportingID:
        raise HTTPException(
            status_code=404, detail="reportedID or reportingID must be given")

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


@router.post("/v1/report", status_code=status.HTTP_201_CREATED, tags=["Report"])
async def insert_report(
    detections: List[detection],
    manual_detect: int = Query(0, ge=0, le=1),
):
    '''
        Inserts detections into to the plugin database.
    '''

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(
        subset=['reporter', 'reported', 'region_id'],
        inplace=True
    )

    sender = list(df["reporter"].unique())

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > int(report_maximum) or df["reporter"].nunique() > 1:
        logger.debug(f'Too Many Reports or Multiple Reporters! | {sender=}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Your sightings are out of bounds. Contact plugin support on our Discord."
        )

    if len(sender[0]) > 12 and not sender[0] == 'AnonymousUser':
        logger.debug(f'invalid username: {sender=}')
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid username. Contact plugin support on our Discord."
        )

    # data validation, checks for correct timing
    now = int(time.time())
    lower_bound = (now - back_time_buffer)
    mask = (df['ts'] > now)
    mask = mask | (df['ts'] < lower_bound)

    if len(df[~mask]) == 0:
        logger.debug(f'Data contains out of bounds time! | {sender=}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Your sightings contain out of bounds time. Contact plugin support on our Discord."
        )

    df = df[~mask]

    # Successful query
    logger.debug(f"Received: {len(df)} from {sender=}")

    # 1) Get a list of unqiue reported names and reporter name
    names = list(df['reported'].unique())
    names.extend(df['reporter'].unique())

    # 1.1) Normalize and validate all names
    clean_names = await jagexify_names_list(names)

    # 2) Get IDs for all unique names
    data = await sql_select_players(clean_names)

    # 3) Create entries for players that do not yet exist in Players table
    existing_names = [d["normalized_name"] for d in data]
    new_names = set([name for name in clean_names]).difference(existing_names)

    # 3.1) Insert new names and get those player IDs from step 3
    if new_names:
        param = [{"name": name, "normalized_name": name} for name in new_names]

        await batch_function(sql_insert_player, param)
        data.extend(await sql_select_players(new_names))

    if len(data) == 0:
        logger.debug(f'Missing player data. | {names=}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your sightings are incomplete. Contact plugin support on our Discord."
        )

    # 4) Insert detections into Reports table with user ids
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)

    df = df.merge(df_names, left_on="reported", right_on="name")

    reporter = [await to_jagex_name(n) for n in df['reporter'].unique()]
    reporter = df_names.query(f"normalized_name == {reporter}")['id'].to_list()

    if len(reporter) == 0:
        logger.debug(f'User does not have a clean name.  | {sender=}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an error processing your name. Contact plugin support on our Discord."
        )

    df["reporter_id"] = reporter[0]
    df['manual_detect'] = manual_detect

    # 4.2) parse data to param
    data = df.to_dict('records')
    param = [await parse_detection(d) for d in data]

    # 4.3) parse query
    await batch_function(sql_insert_report, param)
    return {"detail": "ok"}


@router.get("/v1/report/prediction", tags=["Report", "Business"])
async def get_report_by_prediction(
    token: str,
    label_jagex: int,
    predicted_confidence: int,
    prediction: Optional[str] = None,
    real_player: Optional[int] = None,
    crafting_bot: Optional[int] = None,
    timestamp: Optional[date] = None,
    region_id: Optional[int] = None
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
    timestamp: Optional[date] = None
):
    '''
        get the player count in bulk by region and or date
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
    return data.rows2dict()
