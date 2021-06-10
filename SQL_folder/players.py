# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
# custom
import SQL.functions as functions

def get_player_names(ids=None):
    sql = 'select * from Players;'
    param = None
    
    if not(ids is None):
        sql = 'select * from Players where id in :ids;'
        param = {'ids': ids}

    data = functions.execute_sql(sql, param=param, debug=False)
    return data


def get_player(player_name):
    sql = 'select * from Players where name = :player_name;'
    param = {'player_name': player_name}

    # returns a list of players
    data = functions.execute_sql(sql, param=param, debug=False)

    player = None

    if not(len(data) == 0):
        player = data[0]

    return player


def insert_player(player_name):
    sql_insert = "insert ignore into Players (name) values(:player_name);"

    param = {'player_name': player_name}
    functions.execute_sql(sql_insert, param=param, debug=False, has_return=False)
    player = get_player(player_name)
    return player

# can we make this more dynamic
def update_player(player_id, possible_ban=0, confirmed_ban=0, confirmed_player=0, label_id=0, label_jagex=0, debug=False):
    sql_update = ('''
        update Players 
        set 
            updated_at=:ts, 
            possible_ban=:possible_ban, 
            confirmed_ban=:confirmed_ban, 
            confirmed_player=:confirmed_player, 
            label_id=:label_id,
            label_jagex=:label_jagex
        where 
            id=:player_id;
    ''')

    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    param = {
        'ts':               time_now,
        'possible_ban':     possible_ban,
        'confirmed_ban':    confirmed_ban,
        'confirmed_player': confirmed_player,
        'label_id':         label_id,
        'player_id':        player_id,
        'label_jagex':      label_jagex
    }
    functions.execute_sql(sql_update, param=param, debug=debug, has_return=False)
    
'''
this should be in one QRY?
'''


def get_number_confirmed_bans():
    sql = 'SELECT COUNT(*) bans FROM Players WHERE confirmed_ban = 1;'
    data = functions.execute_sql(sql, param=None, debug=False)
    return data[0].bans


def get_number_tracked_players():
    sql = 'SELECT COUNT(*) count FROM Players;'
    data = functions.execute_sql(sql, param=None, debug=False, has_return=True)
    return data



if __name__ == '__main__':
    print(get_player('extreme4all'))