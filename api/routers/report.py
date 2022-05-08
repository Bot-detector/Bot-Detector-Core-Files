import logging
import time
from datetime import date
from typing import List, Optional

import pandas as pd
from api.database import functions

from api.database.functions import PLAYERDATA_ENGINE
from api.database.models import (Player, Prediction, Report,
                                 playerReports, playerReportsManual, stgReport)
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import Select, insert, select, update

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
    sql = sql.where(
        Player.normalized_name.in_(tuple(await functions.jagexify_names_list(names)))
    )
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)
    data = functions.sqlalchemy_result(data)
    return [] if not data else data.rows2dict()


async def sql_insert_player(new_names: List[dict]) -> None:
    sql = insert(Player)
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql, new_names)


async def sql_insert_report(param: dict) -> None:
    sql = insert(stgReport)
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql, param)


async def parse_detection(data: dict) -> dict:
    gmt = time.gmtime(data["ts"])
    human_time = time.strftime("%Y-%m-%d %H:%M:%S", gmt)

    equipment = data.get("equipment", {})

    param = {
        "reportedID": data.get("id"),
        "reportingID": data.get("reporter_id"),
        "region_id": data.get("region_id"),
        "x_coord": data.get("x_coord"),
        "y_coord": data.get("y_coord"),
        "z_coord": data.get("z_coord"),
        "timestamp": human_time,
        "manual_detect": data.get("manual_detect"),
        "on_members_world": data.get("on_members_world"),
        "on_pvp_world": data.get("on_pvp_world"),
        "world_number": data.get("world_number"),
        "equip_head_id": equipment.get("equip_head_id"),
        "equip_amulet_id": equipment.get("equip_amulet_id"),
        "equip_torso_id": equipment.get("equip_torso_id"),
        "equip_legs_id": equipment.get("equip_legs_id"),
        "equip_boots_id": equipment.get("equip_boots_id"),
        "equip_cape_id": equipment.get("equip_cape_id"),
        "equip_hands_id": equipment.get("equip_hands_id"),
        "equip_weapon_id": equipment.get("equip_weapon_id"),
        "equip_shield_id": equipment.get("equip_shield_id"),
        "equip_ge_value": data.get("equip_ge_value", 0),
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
    regionID: Optional[int] = Query(None, ge=0, le=100000),
):
    """
    Select report data.
    """
    await functions.verify_token(
        token, verification="verify_ban", route="[GET]/v1/report/"
    )

    if None == reportedID == reportingID:
        raise HTTPException(
            status_code=404, detail="reportedID or reportingID must be given"
        )

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
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = functions.sqlalchemy_result(data)
    return data.rows2dict()


@router.put("/v1/report", tags=["Report"])
async def update_reports(old_user_id: int, new_user_id: int, token: str):
    """
    Update the reports from one reporting user to another.
    """
    await functions.verify_token(
        token, verification="verify_ban", route="[PUT]/v1/report/"
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


@router.post("/v1/report", status_code=status.HTTP_201_CREATED, tags=["Report"])
async def insert_report(
    detections: List[detection],
    manual_detect: int = Query(0, ge=0, le=1),
):
    """
    Inserts detections into to the plugin database.
    """

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(subset=["reporter", "reported", "region_id"], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        logger.debug({"message": "Too many reports."})
        return

    # data validation, checks for correct timing
    now = int(time.time())
    now_upper = int(now + 3600)
    now_lower = int(now - 25200)

    df_time = df.ts
    mask = (df_time > now_upper) | (df_time < now_lower)
    if len(df_time[mask].values) > 0:
        logger.debug(
            {
                "message": "Data contains out of bounds time",
                "reporter": df["reporter"].unique(),
                "time": df_time[mask].values[0],
            }
        )
        return

    logger.debug({"message": f"Received: {len(df)} from: {df['reporter'].unique()}"})

    # Normalize names
    df["reporter"] = df["reporter"].apply(
        lambda name: name.lower().replace("_", " ").replace("-", " ").strip()
    )
    df["reported"] = df["reported"].apply(
        lambda name: name.lower().replace("_", " ").replace("-", " ").strip()
    )

    # Get a list of unqiue reported names and reporter name
    names = list(df["reported"].unique())
    names.extend(df["reporter"].unique())

    # validate all names
    valid_names = [name for name in names if await functions.is_valid_rsn(name)]

    # Get IDs for all unique valid names
    data = await sql_select_players(valid_names)

    # Create entries for players that do not yet exist in Players table
    existing_names = [d["normalized_name"] for d in data]
    new_names = set([name for name in valid_names]).difference(existing_names)

    # Get new player id's
    if new_names:
        param = [{"name": name, "nname": name} for name in new_names]
        await functions.batch_function(sql_insert_player, param)
        data.extend(await sql_select_players(new_names))

    # Insert detections into Reports table with user ids
    # add reported & reporter id
    df_names = pd.DataFrame(data)

    if (len(df) == 0) or (len(df_names) == 0):
        logger.debug(
            {"message": "empty dataframe, before merge", "detections": detections}
        )
        return

    df = df.merge(df_names, left_on="reported", right_on="normalized_name")

    if len(df) == 0:
        logger.debug(
            {"message": "empty dataframe, after merge", "detections": detections}
        )
        return

    reporter = df["reporter"].unique()

    if len(reporter) != 1:
        logger.debug({"message": "No reporter", "detections": detections})
        return

    reporter_id = df_names.query(f"normalized_name == {reporter}")["id"].to_list()

    if len(reporter_id) == 0:
        logger.debug({"message": "No reporter in df_names", "detections": detections})
        return

    df["reporter_id"] = reporter_id[0]

    df["manual_detect"] = manual_detect

    # Parse data to param
    data = df.to_dict("records")
    param = [await parse_detection(d) for d in data]

    # Parse query
    await functions.batch_function(sql_insert_report, param)
    return {"detail": "ok"}


@router.get("/v1/report/count", tags=["Report"])
async def get_report_count(name: str):
    """
    Get the calculated player report count
    """
    # query

    voter: Player = aliased(Player, name="voter")
    subject: Player = aliased(Player, name="subject")
    sql: Select = select(
        func.count(playerReports.reported_id),
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player,
    )
    sql = sql.join(voter, playerReports.reporting_id == voter.id)
    sql = sql.join(subject, playerReports.reported_id == subject.id)
    sql = sql.where(voter.name == name)
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


@router.get("/v1/report/manual/count", tags=["Report"])
async def get_report_manual_count(
    name: str
):
    """
    Get the calculated player report count
    """
    # query

    voter:Player = aliased(Player, name="voter")
    subject:Player = aliased(Player, name="subject")

    sql:Select = select(
        func.count(playerReportsManual.reported_id),
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player
    )
    sql = sql.join(voter, playerReportsManual.reporting_id == voter.id)
    sql = sql.join(subject, playerReportsManual.reported_id == subject.id)
    sql = sql.where(voter.name == name)
    sql = sql.group_by(
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player
    )

    keys = ["count","confirmed_ban","possible_ban","confirmed_player"]
    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)
            data = [{k:v for k,v in zip(keys,d)} for d in data]

    return data
