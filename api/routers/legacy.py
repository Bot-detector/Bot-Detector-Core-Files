import logging
import re
import time
from typing import List, Optional

import pandas as pd
from api import Config
from api.database.database import discord_engine
from api.database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm.exc import NoResultFound

'''
This file will have all legacy routes from the Flask api.
after everything is ported, validated & discussed route desing should be done
'''

router = APIRouter()

'''
    models
'''
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

class PlayerName(BaseModel):
    player_name: str

'''
    sql
'''
async def sql_get_player(player_name):
    sql_player_id = 'select * from Players where name = :player_name'

    param = {
        'player_name': player_name
    }

    # returns a list of players
    player = await execute_sql(sql_player_id, param=param, debug=False)
    player = player.rows2dict()

    return None if len(player) == 0 else player[0]


async def sql_insert_player(player_name):
    sql_insert = "insert ignore into Players (name) values(:player_name);"

    param = {
        'player_name': player_name
    }

    await execute_sql(sql_insert, param=param, debug=False)
    player = await sql_get_player(player_name)
    return player


async def sql_insert_report(data):
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    equipment = data.get('equipment').dict()

    param = {
        'reportedID': data.get('reported'),
        'reportingID': data.get('reporter'),
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
        'equip_ge_value': data.get('equipment_ge')
    }

    # list of column values
    columns = list_to_string(list(param.keys()))
    values = list_to_string([f':{column}' for column in list(param.keys())])

    sql = f'insert ignore into Reports ({columns}) values ({values});'

    await execute_sql(sql, param=param, debug=False)
    return


async def sql_get_contributions(contributors: List):
    query = ("""
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
            AND pl.name in :contributors
    """)

    params = {
        "contributors": contributors
    }

    data = await execute_sql(query, param=params, debug=False, row_count=100_000_000)
    return data.rows2dict()

async def sql_get_feedback_submissions(voters: List):
    sql = '''
        SELECT 
            PredictionsFeedback.id
        FROM PredictionsFeedback 
        JOIN Players ON Players.id = PredictionsFeedback.voter_id
        WHERE 1=1
            AND Players.name IN :voters
     '''

    params = {
        "voters": voters
    }

    data = await execute_sql(sql, param=params, debug=False, row_count=100_000_000)
    return data.rows2dict()

async def sql_get_number_tracked_players():
    sql = 'SELECT COUNT(*) count FROM Players'
    data = await execute_sql(sql, param={}, debug=False)
    return data.rows2dict()


async def sql_get_report_stats():
    sql = "SELECT * FROM playerdata.xx_stats"
    data = await execute_sql(sql, param={}, debug=False, )
    return data.rows2dict()


async def sql_get_player_labels():
    sql = 'select * from Labels'
    data = await execute_sql(sql, param={}, debug=False)
    return data.rows2dict()


async def sql_update_player(player: dict):
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    param = player
    param['updated_at'] = time_now

    exclude = ['player_id', 'name']
    values = [f'{k}=:{k}' for k,v in param.items() if v is not None and k not in exclude]
    values = list_to_string(values)

    sql = (f'''
        update Players 
        set
            {values}
        where 
            id=:player_id;
    ''')
    select = "select * from Players where id=:player_id"

    await execute_sql(sql, param)
    data = await execute_sql(select, param)
    return data.rows2dict()


async def sql_get_latest_xp_gain(player_id: int):
    sql = '''          
        SELECT * 
        FROM playerHiscoreDataXPChange xp
        WHERE 1 = 1
            AND xp.Player_id = :player_id
        ORDER BY xp.timestamp DESC
    '''

    param = {
        "player_id": player_id
    }

    data = await execute_sql(sql, param, row_count=2)
    return data.rows2dict()


async def sql_get_discord_verification_status(player_name: str):
    sql = 'SELECT * FROM verified_players WHERE name = :player_name'
    
    param = {
        'player_name': player_name
    }

    data = await execute_sql(sql, param, engine=discord_engine)
    return data.rows2dict()


'''
    helper functions
'''
async def name_check(name):
    bad_name = False
    if len(name) > 13:
        bad_name = True

    temp_name = name
    temp_name = temp_name.replace(' ', '')
    temp_name = temp_name.replace('_', '')
    temp_name = temp_name.replace('-', '')

    if not (temp_name.isalnum()):
        bad_name = True

    return name, bad_name


# TODO: normalize name
async def is_valid_rsn(rsn):
    return True
    return re.fullmatch('[\w\d\s_-]{1,12}', rsn)


# TODO: normalize name
async def to_jagex_name(name: str) -> str:
    return name
    

async def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection['reporter'], bad_name = await name_check(detection['reporter'])
    detection['reported'], bad_name = await name_check(detection['reported'])

    if bad_name:
        Config.debug(
            f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        return 0

    if not (0 <= int(detection['region_id']) <= 15522):
        return 0

    if not (0 <= int(detection['region_id']) <= 15522):
        return 0

    # get reporter & reported
    reporter = await sql_get_player(detection['reporter'])
    reported = await sql_get_player(detection['reported'])

    create = 0
    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = await sql_insert_player(detection['reporter'])
        create += 1

    if reported is None:
        reported = await sql_insert_player(detection['reported'])
        create += 1

    # change in detection
    detection['reported'] = int(reported.id)
    detection['reporter'] = int(reporter.id)

    # insert into reports
    await sql_insert_report(detection)
    return create


async def insync_detect(detections, manual_detect):
    logging.debug("insync detect test")
    total_creates = 0
    for idx, detection in enumerate(detections):
        detection['manual_detect'] = manual_detect

        total_creates += await custom_hiscore(detection)

        if len(detection) > 1000 and total_creates/len(detections) > .75:
            logging.debug(f'    Malicious: sender: {detection["reporter"]}')
            break

        if idx % 500 == 0 and idx != 0:
            logging.debug(f'      Completed {idx + 1}/{len(detections)}')

    logging.debug(f'      Done: Completed {idx + 1} detections')
    return


async def parse_contributors(contributors, version=None):
    contributions = await sql_get_contributions(contributors)

    df = pd.DataFrame(contributions)
    df.drop_duplicates(inplace=True, subset=["reported_ids", "detect"], keep="last")

    try:
        df_detect_manual = df.loc[df['detect'] == 1]

        manual_dict = {
            "reports": len(df_detect_manual.index),
            "bans": int(df_detect_manual['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_manual['possible_ban'].sum()),
            "incorrect_reports": int(df_detect_manual['confirmed_player'].sum())
        }
    except KeyError as e:
        logging.debug(e)
        manual_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0,
            "incorrect_reports": 0
        }

    try:
        df_detect_passive = df.loc[df['detect'] == 0]

        passive_dict = {
            "reports": len(df_detect_passive.index),
            "bans": int(df_detect_passive['confirmed_ban'].sum()),
            "possible_bans": int(df_detect_passive['possible_ban'].sum())
        }
    except KeyError as e:
        logging.debug(e)
        passive_dict = {
            "reports": 0,
            "bans": 0,
            "possible_bans": 0
        }

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

    return return_dict


'''
    routes
'''

async def sql_select_players(names):
    sql = "SELECT * FROM Players WHERE name in :names"
    param = {"names": names}
    data = await execute_sql(sql, param)
    return data.rows2dict()


async def parse_detection(data:dict) ->dict:
    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)

    equipment = data.get('equipment')

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
        'equip_ge_value': data.get('equipment_ge')
    }
    return param


@router.post('/{version}/plugin/detect/{manual_detect}', tags=['legacy'])
async def post_detect(detections: List[detection], version: str = None, manual_detect: int = 0):
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame([d.dict() for d in detections])
    df.drop_duplicates(subset=['reporter', 'reported', 'region_id'], inplace=True)

    # data validation, there can only be one reporter, and it is unrealistic to send more then 5k reports.
    if len(df) > 5000 or df["reporter"].nunique() > 1:
        logging.debug('to many reports')
        return {'NOK': 'NOK'}, 400

    logging.debug(f"Received: {len(df)} from: {df['reporter'].unique()}")

    # 1) Get a list of unqiue reported names and reporter name 
    names = list(df['reported'].unique())
    names.extend(df['reporter'].unique())

    # 1.1) Normalize and validate all names
    clean_names = [await to_jagex_name(name) for name in names if await is_valid_rsn(name)]

    # 2) Get IDs for all unique names
    data = await sql_select_players(clean_names)

    # 3) Create entries for players that do not yet exist in Players table
    existing_names = [d["name"] for d in data]
    new_names = set(clean_names).difference(existing_names)
    
    # 3.1) Get those players' IDs from step 3
    if new_names:
        sql = "insert ignore into Players (name) values(:name)"
        param = [{"name": name} for name in new_names]
        await execute_sql(sql, param)

        data.append(await sql_select_players(new_names))

    # 4) Insert detections into Reports table with user ids 
    # 4.1) add reported & reporter id
    df_names = pd.DataFrame(data)
    df = df.merge(df_names, left_on="reported", right_on="name")
    
    df["reporter_id"]  = df_names.query(f"name == {df['reporter'].unique()}")['id'].to_list()[0]
    # 4.2) parse data to param
    data = df.to_dict('records')
    param = [await parse_detection(d) for d in data]

    # 4.3) parse query
    params = list(param[0].keys())
    columns = list_to_string(params)
    values = list_to_string([f':{column}' for column in params])

    sql = f'insert ignore into Reports ({columns}) values ({values})'
    await execute_sql(sql, param)
    
    return {'OK': 'OK'}


@router.post('/stats/contributions/', tags=['legacy'])
async def get_contributions(contributors: List[contributor]):
    contributors = [d.__dict__['name'] for d in contributors]
    
    data = await parse_contributors(contributors, version=None)
    return data


@router.get('/{version}/stats/contributions/{contributor}', tags=['legacy'])
async def get_contributions_url(contributor: str, version: str):
    data = await parse_contributors([contributor], version=version)
    return data


@router.get('/stats/getcontributorid/{contributor}', tags=['legacy'])
async def get_contributor_id(contributor: str):
    player = await sql_get_player(contributor)

    if player:
        return_dict = {
            "id": player.id
        }

    return return_dict


@router.get('/site/dashboard/projectstats', tags=['legacy'])
async def get_total_reports():
    report_stats = await sql_get_report_stats()

    output = {
        "total_bans": sum(int(r.player_count) for r in report_stats if r.confirmed_ban == 1),
        "total_real_players": sum(int(r.player_count) for r in report_stats \
            if r.confirmed_ban == 0 and r.confirmed_player == 1),
        "total_accounts": sum(int(r.player_count) for r in report_stats)
    }

    return output


@router.get('/labels/get_player_labels', tags=['legacy'])
async def get_player_labels():
    labels = await sql_get_player_labels()
    df = pd.DataFrame(labels)
    return df.to_dict('records')


@router.post('/{version}/plugin/predictionfeedback/', tags=['legacy'])
async def receive_plugin_feedback(feedback: Feedback, version: str = None):
 
    feedback_params = feedback.dict()

    voter_data = await execute_sql(sql=f"select * from Players where name = :player_name", param={"player_name": feedback_params.pop("player_name")})
    voter_data = voter_data.rows2dict()[0]

    feedback_params["voter_id"] = voter_data.get("id")
    exclude = ["player_name"]

    columns = [k for k,v in feedback_params.items() if v is not None and k not in exclude]
    columns = list_to_string(columns)

    values = [f':{k}' for k,v in feedback_params.items() if v is not None and k not in exclude]
    values = list_to_string(values)

    sql = (f'''
        insert ignore into PredictionsFeedback ({columns})
        values ({values}) 
    ''')

    await execute_sql(sql, param=feedback_params, debug=True)
    
    return {"OK": "OK"}


@router.get('/site/highscores/{token}/{ofInterest}', tags=['legacy'])
@router.get('/site/highscores/{token}/{ofInterest}/{row_count}/{page}', tags=['legacy'])
async def get_highscores(
        token: str, 
        ofInterest: int = None, 
        row_count: Optional[int] = 100_000, 
        page: Optional[int] = 1
    ):
    await verify_token(token, verifcation='hiscore')

    if ofInterest is None:
        sql = ('''
            SELECT 
                hdl.*, 
                pl.name 
            FROM playerHiscoreDataLatest hdl 
            inner join Players pl on(hdl.Player_id=pl.id)    
        ''')
    else:
        sql =('''
            SELECT 
                htl.*, 
                poi.name 
            FROM playerHiscoreDataLatest htl 
            INNER JOIN playersOfInterest poi ON (htl.Player_id = poi.id)
        '''
        )

    data = await execute_sql(sql, row_count=row_count, page=page)
    return data.rows2dict()


@router.get('site/players/{token}/{ofInterest}/{row_count}/{page}', tags=['legacy'])
async def get_players(token:str, ofInterest:int=None, row_count:int=100_000, page:int=1):
    await verify_token(token, verifcation='hiscore')

    # get data
    if ofInterest is None:
        sql = 'select * from Players'
    else:
        sql = 'select * from playersOfInterest'

    data = await execute_sql(sql, row_count=row_count, page=page)
    return data.rows2dict()


@router.get('/site/labels/{tokens}', tags=['legacy'])
async def get_labels(token):
    await verify_token(token, verifcation='hiscore')

    sql = 'select * from Labels'
    data = await execute_sql(sql)
    return data.rows2dict()


@router.post('/site/verify/{token}', tags=['legacy'])
async def verify_bot(token:str, bots:bots):
    await verify_token(token, verifcation='ban')

    bots = bots.__dict__
    playerNames = bots['names']
    bot = bots['bot']
    label = bots['label']

    if len(playerNames) == 0:
        raise HTTPException(status_code=405, detail=f"Invalid Parameters")

    data = []
    for name in playerNames:
        user = await sql_get_player(name)

        if user == None:
            continue

        p = dict()
        p['player_id'] = user.id

        if bot == 0 and label == 1:
            # Real player
            p['possible_ban'] = 0
            p['confirmed_ban'] = 0
            p['label_id'] = 1
            p['confirmed_player'] = 1
        else:
            # bot
            p['possible_ban'] = 1
            p['confirmed_ban'] = 1
            p['label_id'] = label
            p['confirmed_player'] = 0
        data.append(await sql_update_player(p))
    return data
    

async def sql_get_unverified_discord_user(player_id):
    sql = ('''
        SELECT * from discordVerification 
        WHERE 1=1
            and Player_id = :player_id 
            and Verified_status = 0
        ''')

    param = {
        "player_id": player_id
    }
    data = await execute_sql(sql, param,engine=discord_engine)
    return data.rows2tuple()


async def sql_get_token(token):
    sql = 'select * from Tokens where token=:token'
    param = {
        'token': token
    }
    data = await execute_sql(sql, param=param)
    return data.rows2dict()


async def set_discord_verification(id, token):
    sql = ('''
        UPDATE discordVerification
        SET
            Verified_status = 1,
            token_used = :token
        where 1=1
            and Entry = :id
    ''')

    param = {
        "id": id,
        "token" : token
    }
    await execute_sql(sql, param, engine=discord_engine)
    return 


@router.post('/{version}/site/discord_user/{token}', tags=['legacy'])
async def verify_discord_user(token:str, discord:discord, version:str=None):
    await verify_token(token, verifcation='verify_players') 
    
    verify_data = discord.dict()
    player = await sql_get_player(verify_data["player_name"])

    if player == None:
        raise HTTPException(status_code=400, detail=f"Could not find player")

    pending_discord = await sql_get_unverified_discord_user(player['id'])

    token_info = await sql_get_token(token)
    token_info = token_info[0]
    token_id = token_info.get('id')

    if pending_discord:
        for record in pending_discord:
            if str(record.Code) == str(verify_data["code"]):
                await set_discord_verification(id=record.Entry, token=token_id)
                break
    else:
        raise HTTPException(status_code=400, detail=f"No pending links for this user.")
    return {'ok':'ok'}


def sort_predictions(d):
    # remove 0's
    d = {key: value for key, value in d.items() if value > 0}
    # sort dict decending
    d = list(sorted(d.items(), key=lambda x: x[1], reverse=True))
    return d


async def sql_get_prediction_player(player_id):
    sql = 'select * from Predictions where id = :id'
    param = {'id':player_id}
    data = await execute_sql(sql, param=param)
    rows_dict = data.rows2dict()
    
    if len(rows_dict) > 0:
        return rows_dict[0]
    else:
        raise NoResultFound
    

@router.get('/{version}/site/prediction/{player_name}', tags=['legacy'])
async def get_prediction(player_name, version=None, token=None):
    player_name, bad_name = await name_check(player_name)

    if bad_name or player_name is None:
        raise HTTPException(status_code=400, detail=f"Bad name")
    
    player = await sql_get_player(player_name)
    try:
        prediction = dict(await sql_get_prediction_player(player['id']))
        prediction.pop("created")

        return_dict = {
            "player_id":                prediction.pop("id"),
            "player_name":              prediction.pop("name"),
            "prediction_label":         prediction.pop("prediction"),
            "prediction_confidence":    prediction.pop("Predicted_confidence")/100
        }

        prediction = {p:float(prediction[p]/100) for p in prediction}

        if version is None:
            return_dict['secondary_predictions'] = sort_predictions(prediction)
        else:
            return_dict['predictions_breakdown'] = prediction

    except NoResultFound:
        return_dict = {
            "player_id": player['id'],
            "player_name": player_name,
            "prediction_label": "No Prediction Yet",
            "prediction_confidence": 0
        }

    return return_dict


###
#  Discord Routes
##
@router.post('/discord/get_xp_gains/{token}', tags=['legacy'])
async def get_latest_xp_gains(player_info:PlayerName, token:str):
    await verify_token(token, verifcation='verify_players')

    player = player_info.dict()
    player_name = player.get('player_name')

    player = await sql_get_player(player_name)
    player_id = player.get('id')

    last_xp_gains = await sql_get_latest_xp_gain(player_id)

    df = pd.DataFrame(last_xp_gains)

    gains_rows_count = len(df.index)


    if(gains_rows_count > 0):

        output = df.to_dict('records')

        output_dict = {
            "latest": output[0],
        }

        if(gains_rows_count == 2):
            output_dict["second"] = output[1]
        elif(gains_rows_count == 1):
            output_dict["second"] = {}
        else:
            return "Server Error: Somehow more than 2 xp gains entries were returned..", 500

        return output_dict
    else:
        return "No gains found for this player.", 404


@router.get('/discord/verify/player_rsn_discord_account_status/{token}/{player_name}', tags=['legacy'])
async def  get_discord_verification_status(token: str, player_name: str):
    await verify_token(token, verifcation='verify_players')

    status_info = await sql_get_discord_verification_status(player_name)

    return status_info

