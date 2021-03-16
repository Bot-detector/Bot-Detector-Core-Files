

from Config import db
from sqlalchemy import text
from collections import namedtuple
import time, random, string


def execute_sql(sql, param=None, debug=False, has_return=True):
    # example
    sql = text(sql)
    if debug:
        print(f'SQL : {sql}')
        print(f'Param: {param}')

    if has_return:
        rows = db.session.execute(sql, param)
        Record = namedtuple('Record', rows.keys())
        records = [Record(*r) for r in rows.fetchall()]

        if debug:
            print(f'keys: {rows.keys()}')
        return records
    else:
        db.session.execute(sql, param)
        db.session.commit()


def get_player(player_name):
    sql_player_id = 'select * from Players where name = :player_name'
    param = {
        'player_name': player_name
    }
    player_id = execute_sql(sql_player_id, param=param, debug=False, has_return=True)
    try:
        return player_id[0]
    except:
        return None


def insert_player(player_name):
    sql_insert = "insert ignore into Players (name) values(:player_name)"

    param = {
        'player_name': player_name
    }

    execute_sql(sql_insert, param=param, debug=False, has_return=False)
    return get_player(player_name)

def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list


def insert_highscore(player_id, skills, minigames):
    columns = list_to_string(
        ['player_id'] + list(skills.keys()) + list(minigames.keys()))
    values = list_to_string(
        [player_id] + list(skills.values()) + list(minigames.values()))

    # f string is not so secure but we control the skills & minigames dict
    sql_insert = f"insert into playerHiscoreData ({columns}) values ({values})"
    execute_sql(sql_insert, param=None, debug=False, has_return=False)


def insert_report(data):
    reporter = insert_player(data['reporter'])
    reported = insert_player(data['reported'])
    param = {
        'reportedID': reporter.id,
        'reportingID': reported.id,
        'region_id': data['region_id'],
        'x_coord': data['x'],
        'y_coord': data['y'],
        'z_coord': data['z'],
        'timestamp': data['ts'],
        'manual_detect': data['manual_detect']
    }

    columns = list_to_string(list(param.keys()))
    sql_insert = f'insert into Reports ({columns}) values (:reportedID, :reportingID, :region_id, :x_coord, :y_coord, :z_coord, :timestamp, :manual_detect)'
    execute_sql(sql_insert, param=param, debug=False, has_return=False)

    return reported.id

def update_player(player_id, possible_ban=0, confirmed_ban=0, confirmed_player=0, label_id=0 ,debug=False):
    sql_update = 'update Players set updated_at=:ts, possible_ban=:possible_ban, confirmed_ban=:confirmed_ban, confirmed_player=:confirmed_player, label_id=:label_id where id=:player_id'
    param = {
        'ts':  time.strftime('%Y-%m-%d %H:%M:%S'),
        'possible_ban': possible_ban,
        'confirmed_ban': confirmed_ban,
        'confirmed_player': confirmed_player,
        'label_id': label_id,
        'player_id': player_id
    }
    execute_sql(sql_update, param=param, debug=debug, has_return=False)

def get_token(token):
    sql = 'select * from Tokens where token=:token'
    param = {
        'token':token
    }
    return execute_sql(sql, param=param, debug=False, has_return=True)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def create_token(player_name, highscores, verify_ban):
    sql_insert = 'insert into tokens (player_name, highscores, verify_ban, token) values (:player_name, :highscores, :verify_ban, :token)'
    token = get_random_string(50)
    param = {
        'player_name':player_name, 
        'highscores':highscores, 
        'verify_ban':verify_ban,
        'token': token
    }
    execute_sql(sql_insert, param=param, debug=False, has_return=True)
    return token

def get_highscores_data():
    sql_highscores = 'select a.*,b.name from playerHiscoreData a left join Players b on (a.Player_id = b.id)'
    highscores = execute_sql(sql_highscores, param=None, debug=False, has_return=True)
    return highscores

def get_player_names():
    sql ='select * from Players'
    data = execute_sql(sql, param=None, debug=False, has_return=True)
    return data