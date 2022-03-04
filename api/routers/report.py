import logging
import time
from datetime import date
from typing import List, Optional

import pandas as pd
from api.database import functions
from api.database.models import Player, Prediction, Report, ReportLatest, stgReport
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy import update
from sqlalchemy.orm import aliased
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
    sql = sql.where(
        Player.normalized_name.in_(tuple(await functions.jagexify_names_list(names)))
    )
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)
    data = functions.sqlalchemy_result(data)
    return [] if not data else data.rows2dict()


async def sql_insert_player(new_names: List[dict]) -> None:
    sql = insert(Player)
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        await session.execute(sql, new_names)
        await session.commit()


async def sql_insert_report(param: dict) -> None:
    sql = insert(stgReport)
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        await session.execute(sql, param)
        await session.commit()


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
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
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
    sql = sql.values(reportingID = new_user_id)
    sql = sql.where(Report.reportingID == old_user_id)

    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        await session.execute(sql)

    return {"OK": "OK"}


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


@router.get("/v1/report/prediction", tags=["Report", "Business"])
async def get_report_by_prediction(
    token: str,
    label_jagex: int,
    predicted_confidence: int,
    prediction: Optional[str] = None,
    real_player: Optional[int] = None,
    crafting_bot: Optional[int] = None,
    timestamp: Optional[date] = None,
    region_id: Optional[int] = None,
):
    """
    Gets account based upon the prediction features.
    Business service: Twitter
    """
    await functions.verify_token(
        token, verification="verify_ban", route="[GET]/v1/report/prediction"
    )

    sql = select(
        Player.id, Prediction.Prediction, Prediction.Predicted_confidence
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
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    output = []
    for row in data:
        mydata = {}
        mydata["id"] = row[0]
        mydata["prediction"] = row[1]
        mydata["Predicted_confidence"] = row[2]
        output.append(mydata)

    return output


@router.get("/v1/report/latest", tags=["Report"])
async def get_latest_report_of_a_user(token: str, reported_id: int = Query(..., ge=0)):

    """
    Select the latest report data, by reported user
    """

    await functions.verify_token(
        token, verification="verify_ban", route="[GET]/v1/report/latest"
    )

    sql = select(ReportLatest)

    if not reported_id is None:
        sql = sql.where(ReportLatest.reported_id == reported_id)

    # execute query
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = functions.sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/report/latest/bulk", tags=["Report"])
async def get_bulk_latest_report_data(
    token: str,
    region_id: Optional[int] = Query(None, ge=0, le=25000),
    timestamp: Optional[date] = None,
):
    """
    get the player count in bulk by region and or date
    """
    await functions.verify_token(
        token, verification="verify_ban", route="[GET]/v1/report/latest/bulk"
    )

    sql = select(ReportLatest)

    if not timestamp is None:
        sql = sql.where(func.date(ReportLatest.timestamp) == timestamp)

    if not region_id is None:
        sql = sql.where(ReportLatest.region_id == region_id)

    # execute query
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = functions.sqlalchemy_result(data)
    return data.rows2dict()


@router.get(
    "/v1/report/count", status_code=status.HTTP_200_OK, tags=["Report", "Business"]
)
async def get_contributions(
    user_name: str = Query(..., min_length=1, max_length=12),
):
    """
    Allows for a player to see their contributions.
    """

    if not await functions.is_valid_rsn(user_name):
        logger.debug(f"Bad Name passed for v1/report/count  | {user_name=}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Your name could not be processed. Contact plugin support on our Discord.",
        )

    user_name = await functions.to_jagex_name(user_name)

    pl = aliased(Player, name="pl")
    ban = aliased(Player, name="ban")

    sql = select(
        func.ifnull(Report.manual_detect, 0),
        ban.confirmed_ban,
        ban.possible_ban,
        ban.confirmed_player,
        func.count(Report.reportedID.distinct()),
    )

    sql = sql.where(pl.normalized_name == user_name)
    sql = sql.group_by(
        Report.manual_detect, ban.confirmed_ban, ban.possible_ban, ban.confirmed_player
    )

    sql = sql.join(pl, pl.id == Report.reportingID)
    sql = sql.join(ban, ban.id == Report.reportedID)

    fields = [
        "manual_detect",
        "confirmed_ban",
        "possible_ban",
        "confirmed_player",
        "count",
    ]
    async with functions.get_session(functions.EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)
    data = [{k: v for k, v in zip(fields, d)} for d in data]

    if len(data) == 0:
        logger.debug(f"No Data found for {user_name=}.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No Data found for {user_name}. Contact Plugin Support on our Discord.",
        )
    return data
