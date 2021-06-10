# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

def get_token(token):
    sql = 'select * from Tokens where token=:token;'
    param = {'token': token}
    return functions.execute_sql(sql, param=param, debug=False)


def create_token(player_name, highscores, verify_ban):
    sql_insert = 'insert into Tokens (player_name, request_highscores, verify_ban, token) values (:player_name, :highscores, :verify_ban, :token);'
    token = functions.get_random_string(15)
    param = {
        'player_name':  player_name,
        'highscores':   highscores,
        'verify_ban':   verify_ban,
        'token':        token
    }
    functions.execute_sql(sql_insert, param=param, debug=False)
    return token