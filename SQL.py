from typing import List
from werkzeug.wrappers import CommonRequestDescriptorsMixin
import Config
import time
import random
import string
from sqlalchemy import text, exc
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
        return

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


def get_players_by_names(names: List[str]):
    sql = f"SELECT * FROM Players WHERE name IN ({','.join(names)})"
    return execute_sql(sql=sql, has_return=True)


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


def insert_multiple_players(names):
    sql_insert = f"insert ignore into Players (name) values {','.join(names)};"
    execute_sql(sql_insert, has_return=False)

    players = get_players_by_names(names)
    return players


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
    return


def update_multiple_players(columns: str, values: list, debug: bool=False):
    sql_update = (f'''
        INSERT INTO Players 
            {columns}
        VALUES
            {",".join(values)}
        ON DUPLICATE KEY UPDATE
            updated_at=VALUES(updated_at),
        	possible_ban=VALUES(possible_ban),
            confirmed_ban=VALUES(confirmed_ban),
            confirmed_player=VALUES(confirmed_player),
            label_id=VALUES(label_id),
            label_jagex=VALUES(label_jagex)
    ''')

    execute_sql(sql=sql_update, param=None, debug=debug, has_return=False)
    return


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
    return


def insert_multiple_highscores(columns: str, values: list, debug: bool=False):
    sql_insert = f'''INSERT IGNORE INTO playerHiscoreData 
                        {columns} 
                     VALUES 
                        {','.join(values)}'''

    execute_sql(sql_insert, param=None, debug=debug, has_return=False)
    return 


def user_latest_xp_gain(player_id):
    sql = '''          
            SELECT * 
            FROM playerHiscoreDataXPChange xp
            WHERE 1 = 1
                AND xp.Player_id = :player_id
            ORDER BY xp.timestamp DESC
            LIMIT 2

        '''
    param = {
        "player_id": player_id
    }

    return execute_sql(sql, param=param, debug=False, has_return=True)


'''
    Reports Table
'''
def user_latest_sighting(player_id):
    sql = '''
            SELECT *
            FROM Reports rpts
            WHERE 1 = 1
                AND rpts.reportedID = :player_id
            ORDER BY rpts.timestamp DESC
            LIMIT 1

        '''
    param = {
        "player_id": player_id
    }

    return execute_sql(sql, param=param, debug=False, has_return=True)

def insert_report(data: List):
    '''
        create the db query based on dict keys
        insert ignore into Reports (col, col col) VALUES (:col, :col, :col)
        colon infront of the col name makes it a variable
    '''
    # list of column values
    columns = list_to_string(list(data[0].keys()))
    values = list_to_string([f':{column}' for column in list(data[0].keys())])

    sql_insert = f'insert ignore into Reports ({columns}) values ({values});'
    execute_sql(sql_insert, param=data, debug=False, has_return=False)
    return


def insert_multiple_reports(columns: list, values: list, debug: bool=False):

    sql_insert = f'''INSERT IGNORE INTO Reports 
                        ({','.join(columns)}) 
                     VALUES 
                        {','.join(values)}'''

    try:
        execute_sql(sql_insert, param=None, debug=debug, has_return=False)
    except exc.OperationalError as e:
        time.sleep(1)
        execute_sql(sql_insert, param=None, debug=debug, has_return=False)

    return 


def transfer_kc(old_id, new_id):

    reports_transfer_sql = f"UPDATE Reports SET reportingID = {new_id} WHERE reporting ID = {old_id};"
    execute_sql(reports_transfer_sql, param=None, debug=False, has_return=False)

    discord_removal_sql = f"DELETE FROM discordVerification WHERE Player_id = {old_id};"
    execute_sql(discord_removal_sql, param=None, debug=False, has_return=False, db_name="discord")

    return


'''
    PredictionFeedback Table
'''


def insert_prediction_feedback(vote_info):
    vote_info.setdefault('feedback_text')
    vote_info.setdefault('proposed_label')

    sql_insert = 'insert ignore into PredictionsFeedback (voter_id, prediction, confidence, vote, subject_id, feedback_text, proposed_label) ' \
                 'values (:voter_id, :prediction, :confidence, :vote, :subject_id, :feedback_text, :proposed_label);'
    execute_sql(sql_insert, param=vote_info, debug=False, has_return=False)

    return


def get_total_feedback_submissions(voters):
    sql = '''SELECT PredictionsFeedback.id
             FROM PredictionsFeedback 
             JOIN Players ON Players.id = PredictionsFeedback.voter_id
             WHERE 1=1
                AND Players.name IN :voters;
     '''

    params = {
        "voters": voters
    }

    return execute_sql(sql, param=params, debug=False, has_return=True)


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


def get_discord_user_link(player_id):
    sql = 'SELECT * from discordVerification WHERE Player_id = :player_id;'

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

def get_count_players_to_scrape():
    sql = "SELECT COUNT(*) FROM playerdata.playersToScrape;"
    return execute_sql(sql, param=None, debug=False, has_return=True)


def get_highscores_data(start=0, amount=1_000_000, name=None):
    param = {
        'start': start,
        'amount': amount
    }

    sql_highscores = (
        '''
        SELECT 
            hdl.*, 
            pl.name 
        FROM playerHiscoreDataLatest hdl 
        inner join Players pl on(hdl.Player_id=pl.id)
        
    ''')
    if name is not None:
        param['name'] = name
        sql_highscores = f'{sql_highscores} where 1=1 and pl.name = :name'
        
    sql_highscores = f'{sql_highscores} LIMIT :start, :amount;'

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
    highscores = execute_sql(sql=sql, param=None, debug=False, has_return=True)
    return highscores


def get_players_to_scrape(start=0, amount=100):
    sql = 'select * from playersToScrape WHERE length(name) <= 12 ORDER BY RAND() LIMIT :start, :amount;'
    param = {'amount': int(amount), 'start': int(start)}
    data = execute_sql(sql, param=param, debug=False, has_return=True)
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
            rs.reported as reported_ids,
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


def get_player_banned_bots(player_name):
    sql = (
        '''
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
        '''
    )

    param = {'player_name': player_name}

    data = execute_sql(sql, param=param, debug=False, has_return=True)
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
        SELECT region_id, x_coord, y_coord, z_coord, confirmed_ban
            FROM Players pls
            JOIN Reports rpts ON rpts.reportedID = pls.id
                WHERE pls.confirmed_ban = 1
                AND rpts.region_id = :region_id
        ORDER BY pls.id DESC LIMIT 100000
                
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
    
  
def get_possible_ban_predicted(amount=1000):
    sql = ('''
        SELECT 
            * 
        FROM playerPossibleBanPrediction 
        WHERE 1=1
            and confirmed_ban = 0
        ORDER BY RAND()
        LIMIT :amount
        
    ''')
    param ={
        'amount':amount
    }
    
    data = execute_sql(sql, param=param, debug=False, has_return=True)
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


def insert_export_link(export_info):
    
    # list of column values
    columns = list_to_string(list(export_info.keys()))
    values = list_to_string([f':{column}' for column in list(export_info.keys())])

    sql_insert = f"INSERT IGNORE INTO export_links ({columns}) VALUES ({values});"

    execute_sql(sql_insert, param=export_info, debug=True, has_return=False, db_name="discord")

    return


def get_export_links(url_text):

    sql = 'SELECT * FROM export_links WHERE url_text IN (:url_text)'
    
    param = {
        'url_text': url_text
    }

    data = execute_sql(sql, param=param, debug=False, has_return=True, db_name="discord")

    return data
    

def update_export_links(update_export):

    sql = '''UPDATE export_links
             SET 
                time_redeemed = :time_redeemed,
                is_redeemed = :is_redeemed
             WHERE id = :id
     '''

    execute_sql(sql, param=update_export, debug=False, has_return=False, db_name="discord")

    return


#Find other OSRS accounts the same user has linked to their Discord ID.
def get_other_linked_accounts(player_name):

    sql = '''
            SELECT
                name
            FROM verified_players
            WHERE 1 = 1
                AND Verified_status = 1
                AND Discord_id IN (
                    SELECT
                        Discord_id
                    FROM verified_players
                    WHERE 1 = 1
                        AND Verified_status = 1
                        AND name = :player_name
                )
          '''

    param = {
        'player_name': player_name
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

def get_player_kc(players):
    sql = ('''
        SELECT
            pl2.name,
            count(DISTINCT rp.reportedID) kc
        FROM Reports rp
        INNER JOIN Players pl ON (rp.reportedID = pl.id)
        INNER JOIN Players pl2 ON (rp.reportingID = pl2.id)
        where 1=1
            and pl2.name in :players
            and pl.confirmed_ban = 1
        GROUP BY
            pl2.name
        '''
    )
    param = {'players': players}
    data = execute_sql(sql, param=param, debug=False, has_return=True)
    return data