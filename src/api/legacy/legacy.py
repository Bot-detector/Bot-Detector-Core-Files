import logging
import os
import pathlib
import random
import re
import string
import time
from typing import List, Optional

import pandas as pd
from src.core import config
from src.database.database import DISCORD_ENGINE, EngineType
from src.database import functions
from src.database.functions import execute_sql, list_to_string, verify_token
from src.utils import logging_helpers
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm.exc import NoResultFound

logger = logging.getLogger(__name__)

"""
This file will have all legacy from the Flask api.
after everything is ported, validated & discussed route desing should be done
"""

router = APIRouter()

"""
    models
"""


class contributor(BaseModel):
    name: str


class equipment(BaseModel):
    equip_head_id: Optional[int]
    equip_amulet_id: Optional[int]
    equip_torso_id: Optional[int]
    equip_legs_id: Optional[int]
    equip_boots_id: Optional[int]
    equip_cape_id: Optional[int]
    equip_hands_id: Optional[int]
    equip_weapon_id: Optional[int]
    equip_shield_id: Optional[int]


class detection(BaseModel):
    reporter: str
    reported: str
    region_id: int
    x: int
    y: int
    z: int
    ts: int
    on_members_world: int
    on_pvp_world: int
    world_number: int
    equipment: Optional[equipment]
    equip_ge_value: Optional[int]


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


class bots(BaseModel):
    bot: int
    label: int
    names: List[str]


class discord(BaseModel):
    player_name: str
    code: str


class ExportInfo(BaseModel):
    discord_id: int
    display_name: str
    file_type: str


class PlayerName(BaseModel):
    player_name: str


class RegionName(BaseModel):
    region_name: str


class RegionID(BaseModel):
    region_id: int


class DiscordVerifyInfo(BaseModel):
    discord_id: int
    player_name: str
    code: int


"""
    sql
"""


async def sql_get_player(player_name: str):
    """Attempts to get data for a player whose names matches player_name."""
    sql_player_id = "select * from Players where normalized_name = :normalized_name"

    param = {"normalized_name": await to_jagex_name(player_name)}

    # returns a list of players
    player = await execute_sql(sql_player_id, param=param)

    try:
        player = player.rows2dict()
        logger.info(f"{player=}, {param=}")
    except AttributeError:
        raise HTTPException(status_code=405, detail="Player does not exist.")

    return None if len(player) == 0 else player[0]


async def sql_insert_player(player_name):
    sql_insert = "insert ignore into Players (name, normalized_name) values (:player_name, :normalized_name);"

    param = {
        "player_name": player_name,
        "normalized_name": await to_jagex_name(player_name),
    }

    await execute_sql(sql_insert, param=param)
    player = await sql_get_player(player_name)
    return player


async def sql_insert_report(data):
    gmt = time.gmtime(data["ts"])
    human_time = time.strftime("%Y-%m-%d %H:%M:%S", gmt)

    equipment = data.get("equipment").dict()

    param = {
        "reportedID": data.get("reported"),
        "reportingID": data.get("reporter"),
        "region_id": data.get("region_id"),
        "x_coord": data.get("x"),
        "y_coord": data.get("y"),
        "z_coord": data.get("z"),
        "timestamp": human_time,
        "manual_detect": data.get("manual_detect"),
        "on_members_world": data.get("on_members_world"),
        "on_pvp_world": data.get("on_pvp_world"),
        "world_number": data.get("world_number"),
        "equip_head_id": equipment.get("HEAD"),
        "equip_amulet_id": equipment.get("AMULET"),
        "equip_torso_id": equipment.get("TORSO"),
        "equip_legs_id": equipment.get("LEGS"),
        "equip_boots_id": equipment.get("BOOTS"),
        "equip_cape_id": equipment.get("CAPE"),
        "equip_hands_id": equipment.get("HANDS"),
        "equip_weapon_id": equipment.get("WEAPON"),
        "equip_shield_id": equipment.get("SHIELD"),
        "equip_ge_value": data.get("equipment_ge"),
    }

    # list of column values
    columns = list_to_string(list(param.keys()))
    values = list_to_string([f":{column}" for column in list(param.keys())])

    sql = f"insert ignore into Reports ({columns}) values ({values});"

    await execute_sql(sql, param=param, debug=False)
    return


async def sql_get_contributions(contributors: List):

    query = """
        SELECT
            rs.manual_detect as detect,
            rs.reportedID as reported_ids,
            ban.confirmed_ban as confirmed_ban,
            ban.possible_ban as possible_ban,
            ban.confirmed_player as confirmed_player
        FROM Reports as rs
        JOIN Players as pl on (pl.id = rs.reportingID)
        join Players as ban on (ban.id = rs.reportedID)
        WHERE 1=1
            AND pl.normalized_name in :contributors
    """

    param = {"contributors": await jagexify_names_list(contributors)}

    output = []

    page = 1
    while True:
        data = await execute_sql(query, param=param, page=page)
        data_dict = data.rows2dict()
        output.extend(data_dict)
        if len(data_dict) < 100_000:
            break
        page += 1

    return output


async def sql_get_feedback_submissions(voters: List):
    sql = """
        SELECT
            PredictionsFeedback.id
        FROM PredictionsFeedback
        JOIN Players ON Players.id = PredictionsFeedback.voter_id
        WHERE 1=1
            AND Players.name IN :voters
     """

    params = {"voters": voters}

    data = await execute_sql(sql, param=params, debug=False, row_count=100_000_000)
    return data.rows2dict() if data is not None else {}


async def sql_get_number_tracked_players():
    sql = "SELECT COUNT(*) count FROM Players"
    data = await execute_sql(sql, param={}, debug=False)
    return data.rows2dict() if data is not None else {}


async def sql_get_report_stats():
    sql = "SELECT * FROM playerdata.xx_stats"
    data = await execute_sql(
        sql,
        param={},
        debug=False,
    )
    return data.rows2dict() if data is not None else {}


async def sql_get_player_labels():
    sql = "select * from Labels"
    data = await execute_sql(sql, param={}, debug=False)
    return data.rows2dict() if data is not None else {}


async def sql_update_player(player: dict):
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    param = player
    param["updated_at"] = time_now

    exclude = ["player_id", "name"]
    values = [
        f"{k}=:{k}" for k, v in param.items() if v is not None and k not in exclude
    ]
    values = list_to_string(values)

    sql = f"""
        update Players
        set
            {values}
        where
            id=:player_id;
    """
    select = "select * from Players where id=:player_id"

    await execute_sql(sql, param)
    data = await execute_sql(select, param)
    return data.rows2dict() if data is not None else {}


async def sql_get_latest_xp_gain(player_id: int):
    sql = """
        SELECT *
        FROM playerHiscoreDataXPChange xp
        WHERE 1 = 1
            AND xp.Player_id = :player_id
        ORDER BY xp.timestamp DESC
    """

    param = {"player_id": player_id}

    data = await execute_sql(sql, param, row_count=2)
    return data.rows2dict()


async def sql_get_discord_verification_status(player_name: str):
    sql = "SELECT * FROM verified_players WHERE name = :player_name"

    param = {"player_name": player_name}

    data = await execute_sql(sql, param, engine=DISCORD_ENGINE)
    return data.rows2dict()


async def sql_get_discord_verification_attempts(player_id: int):
    sql = "SELECT * FROM discordVerification WHERE Player_id = :player_id"

    param = {"player_id": player_id}

    data = await execute_sql(sql, param, engine=DISCORD_ENGINE)
    return data.rows2dict()


async def sql_insert_verification_request(
    discord_id: int, player_id: int, code: int, token_id: int
):
    sql = "INSERT INTO discordVerification (Discord_id, Player_id, Code, token_used) VALUES (:discord_id, :player_id, :code, :token)"

    param = {
        "player_id": player_id,
        "discord_id": discord_id,
        "code": code,
        "token": token_id,
    }

    await execute_sql(sql, param, engine=DISCORD_ENGINE)

    return


async def sql_get_discord_linked_accounts(discord_id: int):
    sql = "SELECT * FROM verified_players WHERE Discord_id = :discord_id and Verified_status = 1"

    param = {"discord_id": discord_id}

    data = await execute_sql(sql, param, engine=DISCORD_ENGINE)
    return data.rows2dict() if data is not None else {}


async def sql_get_user_latest_sighting(player_id: int):
    sql = """
            SELECT *
            FROM Reports rpts
            WHERE 1 = 1
                AND rpts.reportedID = :player_id
            ORDER BY rpts.timestamp DESC
        """
    param = {"player_id": player_id}

    data = await execute_sql(sql, param, row_count=1)
    return data.rows2dict() if data is not None else {}


async def sql_get_report_data_heatmap(region_id: int):
    sql = """
        SELECT region_id, x_coord, y_coord, z_coord, confirmed_ban
            FROM Players pls
            JOIN Reports rpts ON rpts.reportedID = pls.id
                WHERE pls.confirmed_ban = 1
                AND rpts.region_id = :region_id
        ORDER BY pls.id DESC

    """

    param = {"region_id": region_id}

    data = await execute_sql(sql, param, row_count=100_000)
    return data.rows2dict() if data is not None else {}


async def sql_region_search(region_name: str):
    sql = "SELECT * FROM regionIDNames WHERE region_name LIKE :region"

    region_name = "%" + region_name + "%"

    param = {"region": region_name}

    data = await execute_sql(sql, param)
    return data.rows2dict() if data is not None else {}


async def get_ban_spreadsheet_data(player_name: str):
    sql = """
        SELECT
            pl1.name reporter,
            lbl.label,
            hdl.*
        FROM Reports rp
        INNER JOIN Players pl1 ON (rp.reportingID = pl1.id)
        INNER JOIN Players pl2 on (rp.reportedID = pl2.id)
        INNER JOIN Labels lbl ON (pl2.label_id = lbl.id)
        INNER JOIN playerHiscoreDataLatest hdl on (pl2.id = hdl.Player_id)
        where 1=1
            and lower(pl1.name) = :player_name
            and pl2.confirmed_ban = 1
            and pl2.possible_ban = 1
        """

    param = {"player_name": player_name}

    data = await execute_sql(sql, param, row_count=500_000)
    return data.rows2dict() if data is not None else {}


async def insert_export_link(export_info: dict):

    columns = list_to_string(list(export_info.keys()))
    values = list_to_string([f":{column}" for column in list(export_info.keys())])

    sql = f"INSERT IGNORE INTO export_links ({columns}) VALUES ({values});"

    await execute_sql(sql, param=export_info, engine=DISCORD_ENGINE)
    return


async def get_export_link(url_text: str):
    sql = "SELECT * FROM export_links WHERE url_text IN (:url_text)"

    param = {"url_text": url_text}

    data = await execute_sql(sql, param, engine=DISCORD_ENGINE)

    return data.rows2dict() if data is not None else {}


async def update_export_link(update_export: dict):
    sql = """UPDATE export_links
             SET
                time_redeemed = :time_redeemed,
                is_redeemed = :is_redeemed
             WHERE id = :id
     """

    await execute_sql(sql, param=update_export, engine=DISCORD_ENGINE)
    return


"""
    helper functions
"""


async def name_check(name):
    bad_name = False
    if len(name) > 13:
        bad_name = True

    temp_name = name
    temp_name = temp_name.replace(" ", "")
    temp_name = temp_name.replace("_", "")
    temp_name = temp_name.replace("-", "")

    if not (temp_name.isalnum()):
        bad_name = True

    return name, bad_name


# TODO: normalize name
async def is_valid_rsn(rsn):
    # return True
    return re.fullmatch("[\w\d\s_-]{1,12}", rsn)


# TODO: normalize name
async def to_jagex_name(name: str) -> str:
    return name.lower().replace("_", " ").replace("-", " ").strip()


async def jagexify_names_list(names: List[str]) -> List[str]:
    return [await to_jagex_name(n) for n in names if await is_valid_rsn(n)]


async def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection["reporter"], bad_name = await name_check(detection["reporter"])
    detection["reported"], bad_name = await name_check(detection["reported"])

    if bad_name:
        config.debug(
            f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}"
        )
        return 0

    if not (0 <= int(detection["region_id"]) <= 15522):
        return 0

    if not (0 <= int(detection["region_id"]) <= 15522):
        return 0

    # get reporter & reported
    reporter = await sql_get_player(detection["reporter"])
    reported = await sql_get_player(detection["reported"])

    create = 0
    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = await sql_insert_player(detection["reporter"])
        create += 1

    if reported is None:
        reported = await sql_insert_player(detection["reported"])
        create += 1

    # change in detection
    detection["reported"] = int(reported.id)
    detection["reporter"] = int(reporter.id)

    # insert into reports
    await sql_insert_report(detection)
    return create


async def insync_detect(detections, manual_detect):
    logger.debug("insync detect test")
    total_creates = 0
    for idx, detection in enumerate(detections):
        detection["manual_detect"] = manual_detect

        total_creates += await custom_hiscore(detection)

        if len(detection) > 1000 and total_creates / len(detections) > 0.75:
            logger.debug(f'    Malicious: sender: {detection["reporter"]}')
            break

        if idx % 500 == 0 and idx != 0:
            logger.debug(f"      Completed {idx + 1}/{len(detections)}")

    logger.debug(f"      Done: Completed {idx + 1} detections")
    return


async def parse_contributors(
    contributors, version=None, add_patron_stats: bool = False
):
    contributions = await sql_get_contributions(contributors)

    df = pd.DataFrame(contributions)
    df.drop_duplicates(inplace=True, subset=["reported_ids", "detect"], keep="last")

    try:
        df_detect_manual = df.loc[df["detect"] == 1]

        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual["confirmed_ban"].sum()),
            "possible_bans": int(df_detect_manual["possible_ban"].sum()),
            "incorrect_reports": int(df_detect_manual["confirmed_player"].sum()),
        }

        manual_dict["possible_bans"] = (
            manual_dict["possible_bans"] - manual_dict["bans"]
        )

    except KeyError as e:
        logger.debug(e)
        manual_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0,
            "incorrect_reports": 0,
        }

    try:
        df_detect_passive = df.loc[df["detect"] == 0]

        passive_dict = {
            "reports": len(df_detect_passive.index),
            "bans": int(df_detect_passive["confirmed_ban"].sum()),
            "possible_bans": int(df_detect_passive["possible_ban"].sum()),
        }

        passive_dict["possible_bans"] = (
            passive_dict["possible_bans"] - passive_dict["bans"]
        )

    except KeyError as e:
        logger.debug(e)
        passive_dict = {"reports": 0, "bans": 0, "possible_bans": 0}

    total_dict = {
        "reports": passive_dict["reports"] + manual_dict["reports"],
        "bans": passive_dict["bans"] + manual_dict["bans"],
        "possible_bans": passive_dict["possible_bans"] + manual_dict["possible_bans"],
        "feedback": len(await sql_get_feedback_submissions(contributors)),
    }

    if version in ["1.3", "1.3.1"] or None:
        return total_dict

    if add_patron_stats:
        if df.empty:
            total_dict["total_xp_removed"] = 0
        else:
            banned_df = df[df["confirmed_ban"] == 1]
            banned_ids = banned_df["reported_ids"].tolist()

            total_xp_sql = """
                SELECT
                    SUM(total) as total_xp
                FROM playerHiscoreDataLatest
                WHERE Player_id IN :banned_ids
            """

        total_xp_data = await execute_sql(
            sql=total_xp_sql, param={"banned_ids": banned_ids}
        )
        total_xp = total_xp_data.rows2dict()[0].get("total_xp") or 0  # eeewwww
        total_dict["total_xp_removed"] = total_xp

    return_dict = {"passive": passive_dict, "manual": manual_dict, "total": total_dict}

    return return_dict


"""

"""


async def sql_select_players(names: List):
    names = [n.lower() for n in names]
    sql = "SELECT * FROM Players WHERE normalized_name in :names"
    param = {"names": names}
    data = await execute_sql(sql, param)

    return [] if not data else data.rows2dict()


async def parse_detection(data: dict) -> dict:
    gmt = time.gmtime(data["ts"])
    human_time = time.strftime("%Y-%m-%d %H:%M:%S", gmt)

    equipment = data.get("equipment")
    param = {
        "reportedID": data.get("id"),
        "reportingID": data.get("reporter_id"),
        "region_id": data.get("region_id"),
        "x_coord": data.get("x"),
        "y_coord": data.get("y"),
        "z_coord": data.get("z"),
        "timestamp": human_time,
        "manual_detect": data.get("manual_detect"),
        "on_members_world": data.get("on_members_world"),
        "on_pvp_world": data.get("on_pvp_world"),
        "world_number": data.get("world_number"),
        "equip_head_id": equipment.get("HEAD"),
        "equip_amulet_id": equipment.get("AMULET"),
        "equip_torso_id": equipment.get("TORSO"),
        "equip_legs_id": equipment.get("LEGS"),
        "equip_boots_id": equipment.get("BOOTS"),
        "equip_cape_id": equipment.get("CAPE"),
        "equip_hands_id": equipment.get("HANDS"),
        "equip_weapon_id": equipment.get("WEAPON"),
        "equip_shield_id": equipment.get("SHIELD"),
        "equip_ge_value": data.get("equipment_ge"),
    }
    return param


async def detect(detections, manual_detect):
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(subset=["reporter", "reported", "region_id"], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        logger.debug("to many reports")
        return {"NOK": "NOK"}, 400

    logger.debug(f"Received: {len(df)} from: {df['reporter'].unique()}")

    # 1) Get a list of unqiue reported names and reporter name
    names = list(df["reported"].unique())
    names.extend(df["reporter"].unique())

    # 1.1) Normalize and validate all names
    clean_names = await jagexify_names_list(names)

    # 2) Get IDs for all unique names
    data = await sql_select_players(clean_names)

    # 3) Create entries for players that do not yet exist in Players table
    existing_names = [d["name"].lower() for d in data]
    new_names = set([name.lower() for name in clean_names]).difference(existing_names)

    # 3.1) Get those players' IDs from step 3
    if new_names:
        sql = "insert ignore into Players (name) values (:name)"
        param = [{"name": name} for name in new_names]

        await execute_sql(sql, param)

        data.extend(await sql_select_players(new_names))

    # 4) Insert detections into Reports table with user ids
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)
    df = df.merge(df_names, left_on="reported", right_on="name")

    df["reporter_id"] = df_names.query(f"name == {df['reporter'].unique()}")[
        "id"
    ].to_list()[0]
    # 4.2) parse data to param
    data = df.to_dict("records")
    param = [await parse_detection(d) for d in data]

    # 4.3) parse query
    params = list(param[0].keys())
    columns = list_to_string(params)
    values = list_to_string([f":{column}" for column in params])

    sql = f"insert ignore into Reports ({columns}) values ({values})"
    await execute_sql(sql, param)


# @router.post('/{version}/plugin/detect/{manual_detect}', tags=["Legacy"])
# async def post_detect(detections: List[detection], version: str = None, manual_detect: int = 0):
#     #
#     asyncio.to_thread(
#         detect(detections,manual_detect)
#     )
#     # asyncio.create_task(detect(detections, manual_detect))
#     return {'OK': 'OK'}


# @router.post('/stats/contributions/', tags=["Legacy"])
# async def get_contributions(contributors: List[contributor], token: str = None):
#     if token:
#         await verify_token(token, verification='request_highscores')

#         add_patron_stats = True
#     else:
#         add_patron_stats = False


#     contributors = [d.__dict__['name'] for d in contributors]

#     data = await parse_contributors(contributors, version=None, add_patron_stats=add_patron_stats)
#     return data


# @router.get('/{version}/stats/contributions/{contributor}', tags=["Legacy"])
# async def get_contributions_url(contributor: str, version: str):
#     data = await parse_contributors([contributor], version=version)
#     return data


@router.get("/stats/getcontributorid/{contributor}", tags=["Legacy"])
async def get_contributor_id(contributor: str):
    player = await sql_get_player(contributor)

    if player is None:
        player = await sql_insert_player(contributor)

    if player:
        return_dict = {"id": player.id}

    return return_dict


@router.get("/site/dashboard/projectstats", tags=["Legacy"])
async def get_total_reports():
    report_stats = await sql_get_report_stats()

    output = {
        "total_bans": sum(
            int(r.player_count) for r in report_stats if r.confirmed_ban == 1
        ),
        "total_real_players": sum(
            int(r.player_count)
            for r in report_stats
            if r.confirmed_ban == 0 and r.confirmed_player == 1
        ),
        "total_accounts": sum(int(r.player_count) for r in report_stats),
    }

    return output


@router.get("/labels/get_player_labels", tags=["Legacy"])
async def get_player_labels():
    labels = await sql_get_player_labels()
    df = pd.DataFrame(labels)
    return df.to_dict("records")


@router.post("/{version}/plugin/predictionfeedback/", tags=["Legacy"])
async def receive_plugin_feedback(feedback: Feedback, version: str = None):

    feedback_params = feedback.dict()
    player_name = feedback_params.pop("player_name")
    voter_data = await sql_get_player(player_name)

    if voter_data is None:
        voter_data = await sql_insert_player(player_name)

    if not len(voter_data) > 0:
        raise HTTPException(status_code=405, detail=f"Voter does not exist")

    feedback_params["voter_id"] = voter_data.get("id")
    exclude = ["player_name"]

    columns = [
        k for k, v in feedback_params.items() if v is not None and k not in exclude
    ]
    columns = list_to_string(columns)

    values = [
        f":{k}"
        for k, v in feedback_params.items()
        if v is not None and k not in exclude
    ]
    values = list_to_string(values)

    sql = f"""
        insert ignore into PredictionsFeedback ({columns})
        values ({values})
    """

    await execute_sql(sql, param=feedback_params)

    return {"OK": "OK"}


@router.get("/site/highscores/{token}/{ofInterest}", tags=["Legacy"])
@router.get("/site/highscores/{token}/{ofInterest}/{row_count}/{page}", tags=["Legacy"])
async def get_highscores(
    token: str,
    request: Request,
    ofInterest: int = None,
    row_count: Optional[int] = 100_000,
    page: Optional[int] = 1,
):
    await verify_token(
        token,
        verification="request_highscores",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    if ofInterest is None:
        sql = """
            SELECT
                hdl.*,
                pl.name
            FROM playerHiscoreDataLatest hdl
            inner join Players pl on(hdl.Player_id=pl.id)
        """
    else:
        sql = """
            SELECT
                htl.*,
                poi.name
            FROM playerHiscoreDataLatest htl
            INNER JOIN playersOfInterest poi ON (htl.Player_id = poi.id)
        """

    data = await execute_sql(sql, row_count=row_count, page=page)
    return data.rows2dict() if data is not None else {}


@router.get("site/players/{token}/{ofInterest}/{row_count}/{page}", tags=["Legacy"])
async def get_players(
    token: str,
    request: Request,
    ofInterest: int = None,
    row_count: int = 100_000,
    page: int = 1,
):
    await verify_token(
        token,
        verification="request_highscores",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    # get data
    if ofInterest is None:
        sql = "select * from Players"
    else:
        sql = "select * from playersOfInterest"

    data = await execute_sql(sql, row_count=row_count, page=page)
    return data.rows2dict() if data is not None else {}


@router.get("/site/labels/{token}", tags=["Legacy"])
async def get_labels(token, request: Request):
    await verify_token(
        token,
        verification="request_highscores",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    sql = "select * from Labels"
    data = await execute_sql(sql)
    return data.rows2dict() if data is not None else {}


@router.post("/site/verify/{token}", tags=["Legacy"])
async def verify_bot(token: str, bots: bots, request: Request):
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    bots = bots.__dict__
    playerNames = bots["names"]
    bot = bots["bot"]
    label = bots["label"]

    if len(playerNames) == 0:
        raise HTTPException(status_code=405, detail=f"Invalid Parameters")

    data = []
    for name in playerNames:
        user = await sql_get_player(name)

        if user == None:
            continue

        p = dict()
        p["player_id"] = user.id

        if bot == 0 and label == 1:
            # Real player
            p["possible_ban"] = 0
            p["confirmed_ban"] = 0
            p["label_id"] = 1
            p["confirmed_player"] = 1
        else:
            # bot
            p["possible_ban"] = 1
            p["confirmed_ban"] = 1
            p["label_id"] = label
            p["confirmed_player"] = 0
        data.append(await sql_update_player(p))
    return data


async def sql_get_unverified_discord_user(player_id):
    sql = """
        SELECT * from discordVerification
        WHERE 1=1
            and Player_id = :player_id
            and Verified_status = 0
        """

    param = {"player_id": player_id}
    data = await execute_sql(sql, param, engine=DISCORD_ENGINE)
    return data.rows2tuple()


async def sql_get_token(token):
    sql = "select * from Tokens where token=:token"
    param = {"token": token}
    data = await execute_sql(sql, param=param)
    return data.rows2dict() if data is not None else {}


async def set_discord_verification(id, token):
    sql = """
        UPDATE discordVerification
        SET
            Verified_status = 1,
            token_used = :token
        where 1=1
            and Entry = :id
    """

    param = {"id": id, "token": token}
    await execute_sql(sql, param, engine=DISCORD_ENGINE)
    return


@router.post("/{version}/site/discord_user/{token}", tags=["Legacy"])
async def verify_discord_user(
    token: str, discord: discord, request: Request, version: str = None
):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    verify_data = discord.dict()

    code = verify_data.get("code", "")

    if len(code) != 4:
        raise HTTPException(status_code=400, detail=f"Please provide a 4 digit code.")

    try:
        provided_code = int(code)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Please provide a 4 digit code.")

    player = await sql_get_player(verify_data["player_name"])

    if player == None:
        raise HTTPException(status_code=400, detail=f"Could not find player")

    pending_discord = await sql_get_unverified_discord_user(player["id"])

    token_info = await sql_get_token(token)
    token_info = token_info[0]
    token_id = token_info.get("id")

    if not pending_discord:
        raise HTTPException(status_code=400, detail=f"No pending links for this user.")

    found_code = False
    for record in pending_discord:
        if int(record.Code) == provided_code:
            await set_discord_verification(id=record.Entry, token=token_id)
            found_code = True
            break

    if not (found_code):
        raise HTTPException(status_code=400, detail=f"Linking code is incorrect.")

    return {"ok": "ok"}


def sort_predictions(d):
    # remove 0's
    d = {key: value for key, value in d.items() if value > 0}
    # sort dict decending
    d = list(sorted(d.items(), key=lambda x: x[1], reverse=True))
    return d


async def sql_get_prediction_player(player_id):
    sql = "select * from Predictions where id = :id"
    param = {"id": player_id}
    data = await execute_sql(sql, param=param)
    rows_dict = data.rows2dict()

    if len(rows_dict) > 0:
        return rows_dict[0]
    else:
        raise NoResultFound


@router.get("/{version}/site/prediction/{player_name}", tags=["Legacy"])
async def get_prediction(player_name, version=None, token=None):
    player_name, bad_name = await name_check(player_name)

    if bad_name or player_name is None:
        raise HTTPException(status_code=400, detail="Not a valid RSN.")

    player = await sql_get_player(player_name)

    try:
        if player is None:
            raise NoResultFound

        prediction = dict(await sql_get_prediction_player(player["id"]))
        prediction.pop("created")

        return_dict = {
            "player_id": prediction.pop("id"),
            "player_name": prediction.pop("name"),
            "prediction_label": prediction.pop("prediction"),
            "prediction_confidence": prediction.pop("Predicted_confidence") / 100,
        }

        prediction = {p: float(prediction[p] / 100) for p in prediction}

        if version is None:
            return_dict["secondary_predictions"] = sort_predictions(prediction)
        else:
            return_dict["predictions_breakdown"] = prediction

    except NoResultFound:
        return_dict = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "No Prediction Yet",
            "prediction_confidence": 0.0,
        }

    return return_dict


###
#  Discord
##
@router.post("/discord/get_xp_gains/{token}", tags=["Legacy"])
async def get_latest_xp_gains(player_info: PlayerName, token: str, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    player = player_info.dict()
    player_name = player.get("player_name")

    player = await sql_get_player(player_name)

    if player is None:
        raise HTTPException(404, detail="Player not found.")

    player_id = player.get("id")

    last_xp_gains = await sql_get_latest_xp_gain(player_id)

    df = pd.DataFrame(last_xp_gains)

    gains_rows_count = len(df.index)

    if gains_rows_count > 0:

        output = df.to_dict("records")

        output_dict = {
            "latest": output[0],
        }

        if gains_rows_count == 2:
            output_dict["second"] = output[1]
        elif gains_rows_count == 1:
            output_dict["second"] = {}
        else:
            return (
                "Server Error: Somehow more than 2 xp gains entries were returned..",
                500,
            )

        return output_dict
    else:
        return "No gains found for this player.", 404


@router.get(
    "/discord/verify/player_rsn_discord_account_status/{token}/{player_name}",
    tags=["Legacy"],
)
async def get_discord_verification_status_by_name(
    token: str, player_name: str, request: Request
):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    status_info = await sql_get_discord_verification_status(player_name)

    return status_info


@router.get(
    "/discord/verify/get_verification_attempts/{token}/{player_name}", tags=["Legacy"]
)
async def get_discord_verification_attempts(
    token: str,
    player_name: str,
    request: Request,
):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    player = await sql_get_player(player_name)

    if player is None:
        return []

    player_id = player.get("id")

    attempts = await sql_get_discord_verification_attempts(player_id)

    return attempts


@router.post("/discord/verify/insert_player_dpc/{token}", tags=["Legacy"])
async def post_verification_request_information(
    token: str, verify_info: DiscordVerifyInfo, request: Request
):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    info = verify_info.dict()

    player_name = await functions.to_jagex_name(info.get("player_name"))

    discord_id = info.get("discord_id")
    code = info.get("code")

    player = await sql_get_player(player_name)
    if player is None:
        raise HTTPException(404, detail="We've never seen this account before.")

    player_id = player.get("id")

    token_info = await sql_get_token(token)
    token_info = token_info[0]
    token_id = token_info.get("id")

    await sql_insert_verification_request(discord_id, player_id, code, token_id)

    return


@router.get("/discord/get_linked_accounts/{token}/{discord_id}", tags=["Legacy"])
async def get_discord_linked_accounts(token: str, discord_id: int, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    linked_accounts = await sql_get_discord_linked_accounts(discord_id)

    return linked_accounts


@router.post("/discord/get_latest_sighting/{token}", tags=["Legacy"])
async def get_latest_sighting(token: str, player_info: PlayerName, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    player = player_info.dict()
    player_name = player.get("player_name")

    player = await sql_get_player(player_name)
    if player is None:
        raise HTTPException(404, detail="Player not found.")

    player_id = player.get("id")

    last_sighting_data = await sql_get_user_latest_sighting(player_id)

    df = pd.DataFrame(last_sighting_data)

    df = df[
        [
            "equip_head_id",
            "equip_amulet_id",
            "equip_torso_id",
            "equip_legs_id",
            "equip_boots_id",
            "equip_cape_id",
            "equip_hands_id",
            "equip_weapon_id",
            "equip_shield_id",
        ]
    ]

    filtered_sighting = df.to_dict("records")

    return filtered_sighting


@router.post("/discord/region/{token}", tags=["Legacy"])
async def get_region(token: str, region: RegionName, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    region_info = region.dict()
    region_name = region_info.get("region_name")

    regions = await sql_region_search(region_name)

    return regions


@router.post("/discord/heatmap/{token}", tags=["Legacy"])
async def get_heatmap_data(token: str, region_id: RegionID, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    region_data = region_id.dict()
    id = region_data.get("region_id")

    data = await sql_get_report_data_heatmap(id)

    df = pd.DataFrame(data)

    # Remove unnecessary columns
    df = df.drop(columns=["z_coord", "region_id"])

    # Group by tiles
    df = df.groupby(["x_coord", "y_coord"], as_index=False).sum()
    df = df.astype({"confirmed_ban": int})

    output = df.to_dict("records")

    return output


@router.post("/discord/player_bans/{token}", tags=["Legacy"])
async def generate_excel_export(token: str, export_info: ExportInfo, request: Request):
    await verify_token(
        token,
        verification="verify_players",
        route=logging_helpers.build_route_log_string(request, [token]),
    )

    # get_ban_spreadsheet_data
    req_data = export_info.dict()
    discord_id = req_data.get("discord_id")
    display_name = req_data.get("display_name")
    file_type = req_data.get("file_type")

    linked_accounts = await sql_get_discord_linked_accounts(discord_id)

    if len(linked_accounts) == 0:
        raise HTTPException(
            status_code=500, detail="User doesn't have any accounts linked."
        )

    try:
        download_url = await create_ban_export(
            file_type=file_type,
            linked_accounts=linked_accounts,
            display_name=display_name,
            discord_id=discord_id,
        )
    except InvalidFileType:
        raise HTTPException(status_code=400, detail="File type specified is invalid.")
    except NoDataAvailable:
        raise HTTPException(
            status_code=500,
            detail="No ban data available for the linked account(s). Possibly the server timed out.",
        )

    return {"url": download_url}


@router.get("/discord/download_export/{export_id}", tags=["Legacy"])
async def download_export(export_id: str):

    download_data = await get_export_link(export_id)

    if len(download_data) == 0:
        raise HTTPException(
            status_code=400, detail="No export found at the URL provided."
        )
    else:
        file_name = download_data[0].get("file_name")
        file_path = f"{os.getcwd()}/exports/{file_name}"

        if os.path.exists(file_path):

            update_info = {
                "id": download_data[0].id,
                "time_redeemed": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "is_redeemed": 1,
            }

            await update_export_link(update_info)

            return FileResponse(file_path, filename=file_name)

        else:
            raise HTTPException(
                status_code=500,
                detail="File is no longer present on our system. Please use !excelban to generate a new file.",
            )


#
# Excelban helper functions
#


class Error(Exception):
    pass


class NoDataAvailable(Error):
    pass


class InvalidFileType(Error):
    pass


async def create_ban_export(file_type, linked_accounts, display_name, discord_id):

    pathlib.Path(f"{os.getcwd()}/exports/").mkdir(parents=True, exist_ok=True)

    export_data = {}

    export_data["url_text"] = await create_random_link()
    export_data["discord_id"] = discord_id

    if file_type == "csv":
        csv_file_name = await create_csv_export(
            linked_accounts=linked_accounts, display_name=display_name
        )

        export_data["file_name"] = csv_file_name
        export_data["is_csv"] = 1

    elif file_type == "excel":
        excel_file_name = await create_excel_export(
            linked_accounts=linked_accounts, display_name=display_name
        )

        export_data["file_name"] = excel_file_name
        export_data["is_excel"] = 1

    else:
        raise InvalidFileType

    await insert_export_link(export_data)

    return export_data.get("url_text")


async def create_excel_export(linked_accounts, display_name):
    sheets = []
    names = []

    for account in linked_accounts:
        data = await get_ban_spreadsheet_data(account.name)
        df = pd.DataFrame(data)

        sheets.append(df)
        names.append(account.name)

    if len(sheets) > 0:
        totalSheet = pd.concat(sheets)
        totalSheet = totalSheet.drop_duplicates(
            inplace=False, subset=["Player_id"], keep="last"
        )

        file_name = f"{display_name}_bans.xlsx"
        file_path = f"{os.getcwd()}/exports/" + file_name

        writer = pd.ExcelWriter(file_path, engine="xlsxwriter")

        totalSheet.to_excel(writer, sheet_name="Total")

        for idx, name in enumerate(names):
            sheets[idx].to_excel(writer, sheet_name=names[idx])

        writer.save()

        return file_name

    else:
        raise NoDataAvailable


async def create_csv_export(linked_accounts, display_name):
    sheets = []

    for account in linked_accounts:
        data = await get_ban_spreadsheet_data(account.name)
        df = pd.DataFrame(data)

        sheets.append(df)

    totalSheet = pd.concat(sheets)
    totalSheet = totalSheet.drop_duplicates(
        inplace=False, subset=["Player_id"], keep="last"
    )

    file_name = f"{display_name}_bans.csv"
    file_path = f"{os.getcwd()}/exports/" + file_name

    totalSheet.to_csv(file_path, encoding="utf-8", index=False)

    return file_name


async def create_random_link():
    pool = string.ascii_letters + string.digits

    link = "".join(random.choice(pool) for i in range(12))

    return link
