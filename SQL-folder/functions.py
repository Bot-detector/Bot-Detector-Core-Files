# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import string
from sqlalchemy import  text
from collections import namedtuple
# custom
import Config


def execute_sql(sql, param=None, debug=False, db_name="playerdata"):
    engine = Config.db_engines[db_name] # create_engine(sql_uri, poolclass=sqlalchemy.pool.NullPool)

    has_return = True if sql.lower().startswith('select') else False
        
    # parsing
    sql = text(sql)

    # debugging
    if debug:
        Config.debug(f'    SQL : {sql}')
        Config.debug(f'    Param: {param}')

    # make sure that we dont use another engine
    engine.dispose()

    # with handles open and close connection
    with engine.connect() as conn:
        # creates thread save session
        Session = Config.Session(bind=conn) # sqlalchemy.orm.sessionmaker
        session = Session()
        
        # execute session
        rows = session.execute(sql, param)

        # parse data
        if has_return:
            Record = namedtuple('Record', rows.keys())
            records = [Record(*r) for r in rows.fetchall()]
        else:
            records = None

        # commit session
        session.commit()
    return records

def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


if __name__ == '__main__':
    sql = 'SELECT * from Players where name = :name'
    param = {'name':'extreme4all'}
    print(execute_sql(sql, param=param, debug=True))
