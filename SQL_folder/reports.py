# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

import time

def insert_report(data):
    try:
        members = data['on_members_world']
    except KeyError as k:
        members = None

    gmt = time.gmtime(data['ts'])
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', gmt)
    param = {
        'reportedID':       data['reported'],
        'reportingID':      data['reporter'],
        'region_id':        data['region_id'],
        'x_coord':          data['x'],
        'y_coord':          data['y'],
        'z_coord':          data['z'],
        'timestamp':        human_time,
        'manual_detect':    data['manual_detect'],
        'on_members_world': members
    }
    # list of column values
    columns = functions.list_to_string(list(param.keys()))
    values = functions.list_to_string([f':{column}' for column in list(param.keys())])

    sql_insert = f'insert ignore into Reports ({columns}) values ({values});'
    functions.execute_sql(sql_insert, param=param, debug=False)