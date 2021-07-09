from flask_restful import Resource, abort
from sqlalchemy import select
import models
import Config


# TODO: token verification
# abort(404, message="Insufficient permissions")

class Hiscores(Resource):
    def get(self):
        '''
        select form table
        '''
        pass
    
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