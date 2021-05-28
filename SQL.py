from werkzeug.wrappers import CommonRequestDescriptorsMixin
import Config
import time
import random
import string
from sqlalchemy import text
from collections import namedtuple

'''
    Functions for SQL Queries
'''


def name_check(name):
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


def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def execute_sql(sql, param=None, debug=False, has_return=True, db_name="playerdata"):
    engine = Config.db_engines[db_name]
    engine.dispose()
    conn = engine.connect()
    Session = Config.Session(bind=conn)
    session = Session()

    sql = text(sql)
    if debug:
        Config.debug(f'    SQL : {sql}')
        Config.debug(f'    Param: {param}')

    if has_return:
        rows = session.execute(sql, param)
        # db.session.close()
        Record = namedtuple('Record', rows.keys())
        records = [Record(*r) for r in rows.fetchall()]

        if debug:
            print(f'keys: {rows.keys()}')

        session.close()
        conn.close()
        return records
    else:
        session.execute(sql, param)
        session.commit()
        session.close()
        conn.close()

'''
    Players Table
'''


def get_player_names(ids=None):
    if ids is None:
        sql = 'select * from Players;'
        param = None
    else:
        sql = 'select * from Players where id in :ids;'
        param = {'ids':ids}
    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data


def get_player(player_name):
    sql_player_id = 'select * from Players where name = :player_name;'
    param = {
        'player_name': player_name
    }

    # returns a list of players
    player = execute_sql(
        sql=sql_player_id,
        param=param,
        debug=False,
        has_return=True
    )

    if len(player) == 0:
        player_id = None
    else:
        player_id = player[0]

    return player_id


def get_number_confirmed_bans():
    sql = 'SELECT COUNT(*) bans FROM Players WHERE confirmed_ban = 1;'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data[0].bans


def get_number_tracked_players():
    sql = 'SELECT COUNT(*) count FROM Players;'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


def insert_player(player_name):
    sql_insert = "insert ignore into Players (name) values(:player_name);"

    param = {
        'player_name': player_name
    }
    execute_sql(sql_insert, param=param, debug=False, has_return=False)
    player = get_player(player_name)
    return player


def update_player(player_id, possible_ban=None, confirmed_ban=None, confirmed_player=None, label_id=None, label_jagex=None, debug=False):
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    param = {
        'updated_at':       time_now,
        'possible_ban':     possible_ban,
        'confirmed_ban':    confirmed_ban,
        'confirmed_player': confirmed_player,
        'label_id':         label_id,
        'player_id':        player_id,
        'label_jagex':      label_jagex
    }
    
    values = []
    for column in list(param.keys()):
        if column != 'player_id' and param[column] != None:
            values.append(f'{column}=:{column}')

    values = list_to_string(values)

    sql_update = (f'''
        update Players 
        set
            {values}
        where 
            id=:player_id;
        ''')
    
    execute_sql(sql_update, param=param, debug=debug, has_return=False)


'''
    playerHiscoreData Table
'''


def insert_highscore(player_id, skills, minigames):

    keys = []
    keys.append('player_id')
    keys.extend(list(skills.keys()))
    keys.extend(list(minigames.keys()))

    values = []
    values.append(player_id)
    values.extend(list(skills.values()))
    values.extend(list(minigames.values()))

    columns = list_to_string(keys)
    values = list_to_string(values)

    # f string is not so secure but we control the skills & minigames dict
    sql_insert = f"insert ignore into playerHiscoreData ({columns}) values ({values});"
    execute_sql(sql_insert, param=None, debug=False, has_return=False)


'''
    Reports Table
'''


def insert_report(data):
    
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
        'equip_shield_id': data.get('equipment').get('SHIELD') ,
        'equip_ge_value': data.get('equipment_ge')

    }
    # list of column values
    columns = list_to_string(list(param.keys()))
    values = list_to_string([f':{column}' for column in list(param.keys())])

    sql_insert = f'insert ignore into Reports ({columns}) values ({values});'
    execute_sql(sql_insert, param=param, debug=False, has_return=False)


'''
    PredictionFeedback Table
'''


def insert_prediction_feedback(vote_info):
    sql_insert = 'insert ignore into PredictionsFeedback (voter_id, prediction, confidence, vote, subject_id, feedbackText) ' \
                 'values (:voter_id, :prediction, :confidence, :vote, :subject_id, :feedbackText);'
    execute_sql(sql_insert, param=vote_info, debug=False, has_return=False)


'''
    Discord User Table
'''


def get_verified_discord_user(discord_id):
    sql = 'SELECT * from discordVerification WHERE Discord_id = :discord_id ' \
          'AND primary_rsn = 1 ' \
          'AND Verified_status = 1;'

    param = {
        "discord_id": discord_id
    }

    return execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")


def get_unverified_discord_user(player_id):
    sql = 'SELECT * from discordVerification WHERE Player_id = :player_id ' \
          'AND Verified_status = 0;'

    param = {
        "player_id": player_id
    }

    return execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")

def get_all_verified_ids():
    sql = 'SELECT DISTINCT Discord_id FROM verified_players;'

    return execute_sql(sql, param=None, debug=False, has_return=True, db_name="discord")


def set_discord_verification(id, token):

    sql = "UPDATE discordVerification " \
          "SET Verified_status = 1, " \
          "token_used = :token " \
          "WHERE Entry = :id;"

    param = {
        "id": id,
        "token" : token
    }

    return execute_sql(sql, param=param, debug=False, has_return=False, db_name="discord")


'''
    Tokens Table
'''


def get_token(token):
    sql = 'select * from Tokens where token=:token;'
    param = {
        'token': token
    }
    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data[0]


def create_token(player_name, highscores, verify_ban):
    sql_insert = 'insert into Tokens (player_name, request_highscores, verify_ban, token) values (:player_name, :highscores, :verify_ban, :token);'
    token = get_random_string(15)
    param = {
        'player_name': player_name,
        'highscores': highscores,
        'verify_ban': verify_ban,
        'token': token
    }
    execute_sql(sql_insert, param=param, debug=False, has_return=False)
    return token


'''
    Labels Table
'''


def get_player_labels():
    sql = 'select * from Labels;'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


'''
    Queries using Views
'''


def get_highscores_data(start=0, amount=1_000_000):
    sql_highscores = (
        '''
        SELECT 
            hdl.*, 
            pl.name 
        FROM playerHiscoreDataLatest hdl 
        inner join Players pl on(hdl.Player_id=pl.id)
        LIMIT :start, :amount
        ;
    ''')
    param = {
        'start': start,
        'amount': amount
    }
    highscores = execute_sql(sql_highscores, param=param,
                             debug=False, has_return=True)
    return highscores


def get_highscores_data_oneplayer(player_id):
    sql_highscores = (
        '''SELECT 
            hdl.*, 
            pl.name 
        FROM playerHiscoreDataLatest hdl 
        inner join Players pl on(hdl.Player_id=pl.id)
        where Player_id = :player_id
        ;
    ''')
    param  ={
        'player_id':player_id
    }
    highscores = execute_sql(sql=sql_highscores, param=param,
                             debug=False, has_return=True)
    return highscores


def get_hiscores_of_interst():
    sql ='SELECT htl.*, poi.name FROM playerHiscoreDataLatest htl INNER JOIN playersOfInterest poi ON (htl.Player_id = poi.id);'
    highscores = execute_sql(sql=sql, param=None,
                             debug=False, has_return=True)
    return highscores


def get_players_to_scrape(start=None, amount=None):
    sql = 'select * from playersToScrape'
    if not (start is None and amount is None):
        sql = f'{sql} limit {start},{amount}'
    sql = f'{sql};'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


def get_max_players_to_scrape():   
    sql = 'select COUNT(*) as max_players from playersToScrape;'
    data = execute_sql(sql, param=None, debug=True, has_return=True)
    return data

def get_players_of_interest():

    sql = 'select * from playersOfInterest;'

    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


'''
    Joined & complex Queries
'''


def get_report_stats():
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
            ) a;
    '''
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data

# TODO: please clean, add count in query

def get_contributions(contributors):
    
    query = '''
        SELECT
            rs.detect,
            rs.reported as num_reports,
            pl.confirmed_ban as confirmed_ban,
            pl.possible_ban as possible_ban,
            pl.confirmed_player as confirmed_player
        FROM
            (SELECT
                r.reportedID as reported,
                r.manual_detect as detect
        FROM Reports as r
        JOIN Players as pl on pl.id = r.reportingID
        WHERE 1=1
            AND pl.name IN :contributors ) rs
        JOIN Players as pl on (pl.id = rs.reported);
    '''

    params = {
        "contributors": contributors
    }

    data = execute_sql(query, param=params, debug=False, has_return=True)

    return data

def manual_flags_leaderboards():

    query = '''
            SELECT
                pl.confirmed_ban as confirmed_ban,
                pl.possible_ban as possible_ban,
                pl.confirmed_player as confirmed_player
            FROM
                (SELECT
                    r.reportedID as reported,
                    r.manual_detect as detect
            FROM Reports as r
            JOIN Players as pl on pl.id = r.reportingID
            WHERE 1=1
                AND pl.name IN ("Seltzer Bro")
                AND r.manual_detect = 1
            ) rs

            JOIN Players as pl on (pl.id = rs.reported)
        '''


# TODO: route & visual on website
def get_player_table_stats():
    sql = ''' 
        SELECT 
            count(*) Players_checked, 
            Date(updated_at) last_checked_date
        FROM `Players` 
        GROUP BY
            Date(updated_at)
        order BY
            Date(updated_at) DESC
        ;
    '''
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data

# TODO: route & visual on website


def get_hiscore_table_stats():
    sql = ''' 
        SELECT 
            count(*) hiscore_Players_checked, 
            Date(timestamp) hiscore_checked_date
        FROM playerHiscoreData
        GROUP BY
            Date(timestamp)
        order BY
            Date(timestamp) DESC
        ;
    '''
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


def get_region_report_stats():

    sql = '''
        SELECT * FROM `reportedRegion` ORDER BY `reportedRegion`.`region_id` ASC;
    '''

    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data

def get_player_report_locations(players):

    sql = ('''
        SELECT distinct
            pl.name,
            pl.id,
            rin.region_name,
            rp.region_id,
            rp.x_coord,
            rp.y_coord,
            rp.timestamp,
            rp.world_number
        FROM Reports rp
        INNER JOIN Players pl ON (rp.reportedID = pl.id)
        INNER JOIN regionIDNames rin ON (rp.region_id = rin.region_ID)
        where 1
            and pl.name in :players
        ORDER BY
            rp.timestamp DESC
        LIMIT 100000
    ''')

    param = {
        'players': players
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data
    
def get_region_search(regionName):

    sql = "SELECT * FROM regionIDNames WHERE region_name LIKE :region"

    regionName = "%" + regionName + "%"

    param = {
        'region': regionName
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data

def get_all_regions():

    sql = "SELECT * FROM regionIDNames;"

    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data

  
def get_prediction_player(player_id):
    sql = 'select * from Predictions where id = :id'
    param = {'id':player_id}
    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data
    
def get_report_data_heatmap(region_id):

    sql = ('''
        SELECT region_id, x_coord, y_coord, z_coord, confirmed_ban, timestamp
            FROM Reports rpts
            INNER JOIN Players plys ON rpts.reportedID = plys.id 
                WHERE confirmed_ban = 1
                AND region_id = :region_id
    ''')

    param = {
        'region_id': region_id
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data


def get_leaderboard_stats(bans=False, manual=False, limit=25):

    sql = ('''
        SELECT
            pl1.name reporter,
            pl2.name reported
        FROM Reports rp
        INNER JOIN Players pl1 ON (rp.reportingID = pl1.id)
        INNER JOIN Players pl2 on (rp.reportedID = pl2.id)
        where 1=1 AND pl1.name != 'AnonymousUser'
        ''')

    if bans:
        sql += " AND pl2.confirmed_ban = 1"

    if manual:
        sql += " AND rp.manual_detect = 1"

    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data
    
  
def get_possible_ban_predicted():
    sql = 'SELECT * FROM playerPossibleBanPrediction'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data


def get_verification_info(player_name):

    sql = 'SELECT * FROM verified_players WHERE name = :player_name'
    
    param = {
        'player_name': player_name
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")

    return data

def get_verified_info(player_name):

    sql = 'SELECT * FROM verified_players WHERE name = :player_name and Verified_status = 1'
    
    param = {
        'player_name': player_name
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")

    return data

def get_discord_linked_accounts(discord_id):

    sql = 'SELECT * FROM verified_players WHERE Discord_id = :discord_id and Verified_status = 1'
    
    param = {
        'discord_id': discord_id
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")

    return data

def get_verification_player_id(player_name):

    sql = 'SELECT id FROM Players WHERE name = :player_name'
    
    param = {
        'player_name': player_name
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True)

    return data

def verificationInsert(discord_id, player_id, code, token):

    sql = "INSERT INTO discordVerification (Discord_id, Player_id, Code, token_used) VALUES (:discord_id, :player_id, :code, :token)"
    
    param = {
        'player_id': player_id ,
        'discord_id' : discord_id ,
        'code' : code,
        'token' : token
    }
    data = execute_sql(sql, param=param, debug=False, has_return=False, db_name="discord")
    return data

  
def get_prediction_player(player_id):
    sql = 'select * from Predictions where id = :id'
    param = {'id':player_id}
    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data
