# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

def insert_highscore(player_id, skills, minigames):
    # list of column values
    param = skills.update(minigames)
    param = param.update(player_id=player_id)
    columns = functions.list_to_string(list(param.keys()))
    values = functions.list_to_string([f':{column}' for column in list(param.keys())])

    # f string is not so secure but we control the skills & minigames dict
    sql = f"insert ignore into playerHiscoreData ({columns}) values ({values});"
    functions.execute_sql(sql, param=param, debug=False)