

import sqlalchemy
from Config import engine
import models
from flask_restful import Resource, abort
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from collections import namedtuple
from dataclasses import dataclass

engine.echo = True
Session = sessionmaker(engine)


def row2dict(rows):
    return [{col.name: getattr(row, col.name) for col in row.__table__.columns} for row in rows]

def row2tuple(rows):
    # create named tuple
    columns = [col.name for col in rows[0].__table__.columns]
    Record = namedtuple('Record', columns)
    return [Record(*[getattr(row, col.name) for col in row.__table__.columns]) for row in rows]

# TODO: token verification
# abort(404, message="Insufficient permissions")

class Player(Resource):
    def get(self):
        '''
        select form table
        '''
        select_sql = select(models.Player).where(
            models.Player.id <10
        )
        with Session() as session:
            rows = session.execute(select_sql)

         # get data out ChunkedIteratorResult
        rows = [row[0] for row in rows]
        print(f"{row2dict(rows)=}")
        print(f"{row2tuple(rows)=}")
        
        return {'ok':'ok'}
    
    def put(self):
        '''
        Update into table
        '''
        pass

    def post(self):
        '''
        Insert into table
        '''
        pass



