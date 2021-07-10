

from Config import engine
import models
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from sqlalchemy import select, and_
from sqlalchemy.orm import sessionmaker
from Routes.functions import sqlalchemy_result

Session = sessionmaker(engine)

# TODO: token verification
def verify_token(token, access):
    return True
# abort(404, message="Insufficient permissions")

# TODO: swagger support

get_parser = reqparse.RequestParser()
get_parser.add_argument('id', type=int, location='args')
get_parser.add_argument('name', type=str, location='args')
get_parser.add_argument('token', type=str, location='headers')

class Player(Resource):
    def get(self):
        '''
        select from table
        '''
        # parse arguments
        args = get_parser.parse_args()
        verified = verify_token(args['token'], 'hiscores')
        verified_args = []
        
        # convert arguments to sql filter
        filters = []
        for col in args:
            # we cannot filter with None
            if args[col] is None or col == 'token':
                continue

            # verified_args can only be used if you have a valid token
            if not(verified) and col in verified_args:
                continue
            
            # create filter & add filter to list of filters
            filter = (getattr(models.Player, col) == args[col])
            filters.append(filter)

        # abort if no valid filter is given
        if filters == []:
            return abort(404, message="Insufficient arguments")
        
        # create query to execute
        select_sql = select(models.Player).where(
            and_(*filters)
        )

        # create session & execute query
        with Session() as session:
            rows = session.execute(select_sql)
        
        # process & return result
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



