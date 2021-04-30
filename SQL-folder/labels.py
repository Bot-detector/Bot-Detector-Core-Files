# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

def get_player_labels():
    sql = 'select * from Labels;'
    data = functions.execute_sql(sql, param=None, debug=False)
    return data