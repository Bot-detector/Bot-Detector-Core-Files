# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

def get_verified_discord_user(discord_id):
    sql = (
        '''
        SELECT * from discordVerification 
        WHERE 1=1
            and Discord_id = :discord_id
            and primary_rsn = 1
            and Verified_status = 1;
        '''
    )

    param = {"discord_id": discord_id}

    return functions.execute_sql(sql, param=param, debug=False, db_name="discord")


def get_unverified_discord_user(player_id):
    sql = (
        '''
        SELECT * from discordVerification 
        WHERE 1=1
            and Player_id = :player_id
            and Verified_status = 0;
        '''
    )

    param = {"player_id": player_id}

    return functions.execute_sql(sql, param=param, debug=False, db_name="discord")


def set_discord_verification(id):
    sql = (
        '''
        UPDATE discordVerification 
        set
            Verified_status = 1
        where 1=1
            and Entry = :id;
        '''
    )

    param = {"id": id}

    return functions.execute_sql(sql, param=param, debug=False, db_name="discord")