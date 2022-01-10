
import logging
import time
from datetime import date
from typing import List, Optional

import pandas as pd
from api.Config import (back_time_buffer, front_time_buffer, report_maximum,
                        upper_gear_cost)
from api.database.functions import (EngineType, batch_function, create_task,
                                    get_session, is_valid_rsn, list_to_string,
                                    parse_detection, sql_insert_player,
                                    sql_insert_report, sql_select_players,
                                    sqlalchemy_result, to_jagex_name,
                                    verify_token)
from api.database.models import (Player, Prediction, Report, ReportLatest,
                                 stgReport)
from api.routers.legacy_debug import detect
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import insert, select

logger = logging.getLogger(__name__)
router = APIRouter()


class equipment(BaseModel):
    equip_head_id: int = Query(None, ge=0)
    equip_amulet_id: int = Query(None, ge=0)
    equip_torso_id: int = Query(None, ge=0)
    equip_legs_id: int = Query(None, ge=0)
    equip_boots_id: int = Query(None, ge=0)
    equip_cape_id: int = Query(None, ge=0)
    equip_hands_id: int = Query(None, ge=0)
    equip_weapon_id: int = Query(None, ge=0)
    equip_shield_id: int = Query(None, ge=0)


class detections(BaseModel):
    reporter: str = Query(..., min_length=1, max_length=12)
    reported: str = Query(..., min_length=1, max_length=12)
    region_id: int = Query(0, ge=0)
    x_coord: int = Query(0, ge=0)
    y_coord: int = Query(0, ge=0)
    z_coord: int = Query(0, ge=0)
    ts: int = Query(0, ge=0)
    manual_detect: int = Query(0, ge=0, le=1)
    on_members_world: int = Query(0, ge=0, le=1)
    on_pvp_world: int = Query(0, ge=0, le=1)
    world_number: int = Query(0, ge=0, le=1000)
    equipment: equipment
    equip_ge_value: int = Query(0, ge=0, le=int(upper_gear_cost))


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


@router.post("/v1/report", tags=["Report"])
async def insert_report(
    detections: List[detections],
    manual_detect: int = Query(0, ge=0, le=1),
    ):
    
    '''
        Inserts detections to the plugin database.
    '''

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(
        subset=['reporter', 'reported', 'region_id'], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > int(report_maximum) or df["reporter"].nunique() > 1:
        logger.warning('Too Many Reports or Multiple Reporters!')
        raise HTTPException(status_code=400, detail="{'error':'One or more of the values that you have sent are out of bounds.'}")

    # data validation, checks for correct timing
    now = int(time.time())
    df_time = df.ts
    mask = (df_time > int(now + int(front_time_buffer))) | (df_time < int(now - int(back_time_buffer)))
    if len(df_time[mask].values) > 0:
        logger.warning(f'Data contains out of bounds time!')
        raise HTTPException(status_code=400, detail="{'error':'One or more of the values that you have sent are out of bounds.'}")

    # Successful query
    logger.debug(f"Received: {len(df)} from: {df['reporter'].unique()}")

    # 1) Get a list of unqiue reported names and reporter name
    names = list(df['reported'].unique())
    names.extend(df['reporter'].unique())

    # 1.1) Normalize and validate all names
    clean_names = [await to_jagex_name(name) for name in names if await is_valid_rsn(name)]

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

    # 4) Insert detections into Reports table with user ids
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)

    try:
        df = df.merge(df_names, left_on="reported", right_on="name")
    except KeyError:
        logger.debug(f'Key Error: {df} '+f'{df.columns}')
        raise HTTPException(status_code=400, detail="There was an error in the data you've sent to us.")

    reporter = [await to_jagex_name(n) for n in df['reporter'].unique()]

    try:
        df["reporter_id"] = df_names.query(f"normalized_name == {reporter}")['id'].to_list()[0]
    except IndexError as ie:
        raise HTTPException(status_code=400, detail="There was an error in the data you've sent to us.")

    df['manual_detect'] = manual_detect
    # 4.2) parse data to param
    data = df.to_dict('records')
    param = [await parse_detection(d) for d in data]

    # 4.3) parse query
    await batch_function(sql_insert_report, param)
    return {"OK": "OK"}


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
