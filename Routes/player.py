

import sqlalchemy
from Config import engine
import models
from flask_restful import Resource, abort
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

engine.echo = True
Session = sessionmaker(engine)



# TODO: token verification
# abort(404, message="Insufficient permissions")

class Player(Resource):
    def get(self):
        '''
        select form table
        '''
        select_player = (select(models.Player).where(
            models.Player.id == 1
        ))

        with Session() as session:
            rows = session.query(models.Player).first()
            print(f'{rows=}')
            # Record = namedtuple('Record', rows.keys())
            # records = [Record(*r) for r in rows.fetchall()]

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



