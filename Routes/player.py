

import sqlalchemy
from Config import engine
import models
from flask_restful import Resource, abort
from flask import jsonify
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from Routes.functions import sqlalchemy_result


engine.echo = True
Session = sessionmaker(engine)

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
        
        rows = sqlalchemy_result(rows)
        return jsonify(rows.rows2dict())
    
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



