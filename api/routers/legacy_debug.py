import asyncio
import logging
import re
import time
from typing import List, Optional

import pandas as pd
from api.Config import app
from api.database.functions import (batch_function, execute_sql,
                                    list_to_string, verify_token)
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)


'''DETECT ROUTE'''
class equipment(BaseModel):
    HEAD: Optional[int]
    AMULET: Optional[int]
    TORSO: Optional[int]
    LEGS: Optional[int]
    BOOTS: Optional[int]
    CAPE: Optional[int]
    HANDS: Optional[int]
    WEAPON: Optional[int]
    SHIELD: Optional[int]


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
    equipment_ge: Optional[int]


async def is_valid_rsn(rsn: str) -> bool:
    return re.fullmatch('[\w\d\s_-]{1,13}', rsn)


async def to_jagex_name(name: str) -> str:
    return name.lower().replace('_', ' ').replace('-',' ').strip()


async def jagexify_names_list(names: List[str]) -> List[str]:
    return  [await to_jagex_name(n) for n in names if await is_valid_rsn(n)]


async def sql_select_players(names):
    sql = "SELECT * FROM Players WHERE normalized_name in :names"
    param = {"names": tuple(await jagexify_names_list(names))}
    data = await execute_sql(sql, param)
    
    return [] if not data else data.rows2dict()


async def parse_detection(data:dict) -> dict:
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    equipment = data.get('equipment', {})

    param = {
        'reportedID': data.get('id'),
        'reportingID': data.get('reporter_id'),
        'region_id': data.get('region_id'),
        'x_coord': data.get('x'),
        'y_coord': data.get('y'),
        'z_coord': data.get('z'),
        'timestamp': human_time,
        'manual_detect': data.get('manual_detect'),
        'on_members_world': data.get('on_members_world'),
        'on_pvp_world': data.get('on_pvp_world'),
        'world_number': data.get('world_number'),
        'equip_head_id': equipment.get('HEAD'),
        'equip_amulet_id': equipment.get('AMULET'),
        'equip_torso_id': equipment.get('TORSO'),
        'equip_legs_id': equipment.get('LEGS'),
        'equip_boots_id': equipment.get('BOOTS'),
        'equip_cape_id': equipment.get('CAPE'),
        'equip_hands_id': equipment.get('HANDS'),
        'equip_weapon_id': equipment.get('WEAPON'),
        'equip_shield_id': equipment.get('SHIELD'),
        'equip_ge_value': data.get('equipment_ge', 0)
    }
    return param


async def sql_insert_player(param):
    sql = "INSERT ignore INTO Players (name, normalized_name) VALUES (:name, :nname)"
    await execute_sql(sql, param)


async def sql_insert_report(param):
    params = list(param[0].keys())
    columns = list_to_string(params)
    values = list_to_string([f':{column}' for column in params])

    sql = f'INSERT ignore INTO stgReports ({columns}) VALUES ({values})'
    await execute_sql(sql, param)


async def detect(detections:List[detection], manual_detect:int) -> None:
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(subset=['reporter', 'reported', 'region_id'], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        logger.debug('Too many reports.')
        return {'ERROR': 'ERROR'}, 400
    
    # data validation, checks for correct timing
    now = int(time.time())
    now_upper = int(now + 3600)
    now_lower = int(now - 3600)

    df_time = df.ts
    mask = (df_time > now_upper) | (df_time < now_lower)
    if len(df_time[mask].values) >= 0:
        logger.debug(f'Data contains out of bounds time. {df_time[mask].values}')
        return {'ERROR': 'ERROR'}, 400


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
    
    # 3.1) Get those players' IDs from step 3
    if new_names:
        param = [{"name": name, "nname":name} for name in new_names]
        await batch_function(sql_insert_player, param)

        data.extend(await sql_select_players(new_names))

    # 4) Insert detections into Reports table with user ids 
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)
    
    
    try:
        df = df.merge(df_names, left_on="reported", right_on="name")
    except KeyError:
        logger.debug(f'Key Error: {df} '+f'{df.columns}')
        raise KeyError(f"There was a key error with this entry.")

    reporter = [await to_jagex_name(n) for n in df['reporter'].unique()]

    try:
        df["reporter_id"] = df_names.query(f"normalized_name == {reporter}")['id'].to_list()[0]
    except IndexError as ie:
        raise IndexError(f"Detection Submission Error: {reporter} was not found in {df_names}.")


    df['manual_detect'] = manual_detect
    # 4.2) parse data to param
    data = df.to_dict('records')
    param = [await parse_detection(d) for d in data]

    # 4.3) parse query
    await batch_function(sql_insert_report, param)


async def offload_detect(detections:List[detection], manual_detect:int) -> None:
    await run_in_process(detect, detections, manual_detect)


@router.post('/{version}/plugin/detect/{manual_detect}', tags=["Legacy"])
async def post_detect(
        detections:List[detection],
        version:str=None, 
        manual_detect:int=0
    ):
    asyncio.create_task(
        detect(detections, manual_detect)
    )
    return {'ok':'ok'}


'''CONTRIBUTIONS ROUTE'''
class contributor(BaseModel):
    name: str


async def sql_get_contributions(contributors: List):

    query = ("""
        SELECT
            ifnull(rs.manual_detect,0) as detect,
            rs.reportedID as reported_ids,
            ban.confirmed_ban as confirmed_ban,
            ban.possible_ban as possible_ban,
            ban.confirmed_player as confirmed_player
        FROM Reports as rs
        JOIN Players as pl on (pl.id = rs.reportingID)
        join Players as ban on (ban.id = rs.reportedID)
        WHERE 1=1
            AND pl.normalized_name in :contributors
    """)

    param = {
        "contributors": tuple(await jagexify_names_list(contributors))
    }

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
    sql = '''
        SELECT 
            PredictionsFeedback.id
        FROM PredictionsFeedback 
        JOIN Players ON Players.id = PredictionsFeedback.voter_id
        WHERE 1=1
            AND Players.normalized_name IN :voters
     '''

    params = {
        "voters": tuple(await(jagexify_names_list(voters)))
    }

    data = await execute_sql(sql, param=params, row_count=100_000_000)
    return data.rows2dict()


async def parse_contributors(contributors, version=None, add_patron_stats:bool=False):
    contributions = await sql_get_contributions(contributors)

    df = pd.DataFrame(contributions)

    df.drop_duplicates(inplace=True, subset=["reported_ids", "detect"], keep="last")

    if df.empty:
        manual_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0,
            "incorrect_reports": 0
        }

        passive_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0
        }

        total_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0,
            'feedback': 0
        }

    else:
        df_detect_manual = df.loc[df['detect'] == 1]
        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_manual['possible_ban'].sum()),
            "incorrect_reports": int(df_detect_manual['confirmed_player'].sum())
        }
        manual_dict["possible_bans"] = manual_dict["possible_bans"] - manual_dict["bans"]

        df_detect_passive = df.loc[df['detect'] == 0]

        passive_dict = {
            "reports": len(df_detect_passive.index),
            "bans": int(df_detect_passive['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_passive['possible_ban'].sum())
        }
        passive_dict["possible_bans"] = passive_dict["possible_bans"] - passive_dict["bans"]

        total_dict = {
            "reports": passive_dict['reports'] + manual_dict['reports'],
            "bans": passive_dict['bans'] + manual_dict['bans'],
            "possible_bans": passive_dict['possible_bans'] + manual_dict['possible_bans'],
            'feedback': len(await sql_get_feedback_submissions(contributors))
        }

    if version in ['1.3','1.3.1'] or None:
        return total_dict

    return_dict = {
        "passive": passive_dict,
        "manual": manual_dict,
        "total": total_dict
    }

    if not add_patron_stats:
        return return_dict
    
    total_dict["total_xp_removed"] = 0
    
    if df.empty:
        return_dict['total'] = total_dict
        return return_dict
 
    banned_df = df[df["confirmed_ban"] == 1]
    banned_ids = banned_df["reported_ids"].tolist()

    total_xp_sql = '''
        SELECT
            SUM(total) as total_xp
        FROM playerHiscoreDataLatest
        WHERE Player_id IN :banned_ids
    '''

    total_xp_data = await execute_sql(sql=total_xp_sql, param={"banned_ids": tuple(banned_ids)})
    
    if not total_xp_data:
        return_dict['total'] = total_dict
        return return_dict

    total_xp = total_xp_data.rows2dict()[0].get("total_xp", 0)
    total_dict["total_xp_removed"] = total_xp
    return_dict['total'] = total_dict
    return return_dict


@router.post('/stats/contributions/', tags=["Legacy"])
async def get_contributions(contributors: List[contributor], token:str=None):
    add_patron_stats = False
    if token:
        await verify_token(token, verification='verify_players')
        add_patron_stats = True
        
    accounts = [await to_jagex_name(d.__dict__['name']) for d in contributors]
    
    data = await parse_contributors(accounts, version=None, add_patron_stats=add_patron_stats)
    return data


@router.get('/{version}/stats/contributions/{contributor}', tags=["Legacy"])
async def get_contributions_url(contributor: str, version: str):
    data = await parse_contributors([await to_jagex_name(contributor)], version=version)
    return data
