from collections import namedtuple

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, with_expression

from .database import engine
import logging



def list_to_string(l):
    string_list = ', '.join(str(item) for item in l)
    return string_list
    
def execute_sql(sql, param=None, debug=False, engine=engine):
    has_return = True if sql.lower().startswith('select') else False
    # parsing
    sql = text(sql)

    # debugging
    if debug:
        logging.debug(f'{has_return=}')
        logging.debug(f'sql={sql.compile(engine)}')
        logging.debug(f'{param=}')
    
    # make sure that we dont use another engine
    engine.dispose()

    # with handles open and close connection
    with engine.connect() as conn:
        # creates thread save session
        Session = sessionmaker(conn)
        with Session() as session:
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


'''
just in case wee need it later
'''

class sqlalchemy_result:
    def __init__(self, rows):
        self.rows = [row[0] for row in rows]

    def rows2dict(self):
        return [{col.name: getattr(row, col.name) for col in row.__table__.columns} for row in self.rows]

    def rows2tuple(self):
        columns = [col.name for col in self.rows[0].__table__.columns]
        Record = namedtuple('Record', columns)
        return [Record(*[getattr(row, col.name) for col in row.__table__.columns]) for row in self.rows]
