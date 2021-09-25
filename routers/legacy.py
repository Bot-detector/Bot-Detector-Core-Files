import logging
import time
from typing import List, Optional

import Config
import pandas as pd
import SQL
from database.functions import execute_sql, list_to_string, verify_token
from database.database import discord_engine
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
    reporter: str
    reported: str
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
        'equip_head_id': data.get('equipment').get('HEAD'),
        'equip_amulet_id': data.get('equipment').get('AMULET'),
        'equip_torso_id': data.get('equipment').get('TORSO'),
        'equip_legs_id': data.get('equipment').get('LEGS'),
        'equip_boots_id': data.get('equipment').get('BOOTS'),
        'equip_cape_id': data.get('equipment').get('CAPE'),
        'equip_hands_id': data.get('equipment').get('HANDS'),
        'equip_weapon_id': data.get('equipment').get('WEAPON'),
        'equip_shield_id': data.get('equipment').get('SHIELD'),
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
            pl.confirmed_ban as confirmed_ban,
            pl.possible_ban as possible_ban,
            pl.confirmed_player as confirmed_player
        FROM Reports as rs
        JOIN Players as pl on (pl.id = rs.reportingID)
        WHERE 1=1
            AND pl.name in :contributors
    """)

    params = {
        "contributors": contributors
    }

    data = await execute_sql(query, param=params, debug=False, row_count=100_000_000)
    return data.rows2dict()

async def sql_get_number_tracked_players():
    sql = 'SELECT COUNT(*) count FROM Players'
    data = await execute_sql(sql, param=None, debug=False)
    return data.rows2dict()

async def sql_get_report_stats():
    sql = '''
        SELECT
            sum(bans) bans,
            sum(false_reports) false_reports,
            sum(bans) + sum(false_reports) total_reports,
            sum(bans)/ (sum(bans) + sum(false_reports)) accuracy
        FROM (
            SELECT 
                confirmed_ban,
                sum(confirmed_ban) bans,
                sum(confirmed_player) false_reports
            FROM Players
            GROUP BY
                confirmed_ban
            ) a
    '''
    data = await execute_sql(sql, param=None, debug=False)
    return data.rows2dict()

async def sql_get_player_labels():
    sql = 'select * from Labels'
    data = await execute_sql(sql, param=None, debug=False)
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

async def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection['reporter'], bad_name = name_check(detection['reporter'])
    detection['reported'], bad_name = name_check(detection['reported'])

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
        "possible_bans": passive_dict['possible_bans'] + manual_dict['possible_bans']
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
@router.post('/{version}/plugin/detect/{manual_detect}', tags=['legacy'])
async def post_detect(detections: List[detection], version: str = None, manual_detect: int = 0):
    manual_detect = 0 if int(manual_detect) == 0 else 1

    # remove duplicates
    df = pd.DataFrame([d.__dict__ for d in detections])
    df.drop_duplicates(subset=['reporter', 'reported', 'region_id'], inplace=True)

    if len(df) > 5000 or df["reporter"].nunique() > 1:
        logging.debug('to many reports')
        return {'NOK': 'NOK'}, 400

    detections = df.to_dict('records')

    logging.debug(f'      Received detections: DF shape: {df.shape}')
    # Config.sched.add_job(insync_detect, args=[detections, manual_detect], replace_existing=False, name='detect')
    return {'OK': 'OK'}

@router.post('/stats/contributions/', tags=['legacy'])
async def get_contributions(contributors: List[contributor]):
    contributors = [d.__dict__['name'] for d in contributors]
    
    data = await parse_contributors(contributors, version=None)
    return data

@router.get('/{version}/stats/contributions/{contributor}', tags=['legacy'])
async def get_contributions(contributors: str, version: str):
    data = await parse_contributors([contributors], version=version)
    return data

@router.get('/stats/getcontributorid/{contributor}', tags=['legacy'])
async def get_contributor_id(contributor: str):
    player = await sql_get_player(contributor)

    if player:
        return_dict = {
            "id": player.id
        }

    return return_dict

@router.get('/site/dashboard/gettotaltrackedplayers', tags=['legacy'])
async def get_total_tracked_players():
    num_of_players = await sql_get_number_tracked_players()
    return {"players": num_of_players[0]}

@router.get('/site/dashboard/getreportsstats', tags=['legacy'])
async def get_total_reports():
    report_stats = await sql_get_report_stats()[0]

    output = {
        "bans": int(report_stats[0]),
        "false_reports": int(report_stats[1]),
        "total_reports": int(report_stats[2]),
        "accuracy": float(report_stats[3])
    }

    return output

@router.get('/labels/get_player_labels', tags=['legacy'])
async def get_player_labels():
    labels = sql_get_player_labels()
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

@router.get("/log/{token}", tags=['legacy'])
async def print_log(token:str):
    await verify_token(token, verifcation='ban')
    return FileResponse(path='error.log', filename='error.log', media_type='text/log')

@router.get('/site/highscores/{token}/{ofInterest}/{row_count}/{page}', tags=['legacy'])
async def get_highscores(token:str, ofInterest:int=None, row_count:int=100_000, page:int=1):
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
    return data.rows2tuple()[0]

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

    token_id = await sql_get_token(token).id

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
    return data.rows2dict()[0]

@router.get('/{version}/site/prediction/{player_name}/{token}', tags=['legacy'])
async def get_prediction(player_name, version=None, token=None):
    player_name, bad_name = await name_check(player_name)
    if bad_name:
        raise HTTPException(status_code=400, detail=f"Bad name")
    
    player = await sql_get_player(player_name)
    prediction = dict(await sql_get_prediction_player(player['id']))
    prediction.pop("created")

    return_dict = {
        "player_id":                prediction.pop("id"),
        "player_name":              prediction.pop("name"),
        "prediction_label":         prediction.pop("prediction"),
        "prediction_confidence":    prediction.pop("Predicted_confidence"),
        #"predictions_breakdown":    prediction_dict
    }
    if version is None:
        return_dict['secondary_predictions'] = sort_predictions(prediction)
    else:
        return_dict['predictions_breakdown'] = prediction
    return return_dict
