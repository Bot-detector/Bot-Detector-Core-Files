from flask import Blueprint
from flask.json import jsonify
import SQL

discord = Blueprint('discord', __name__, template_folder='templates')


@discord.route('/discord/locations/<token>/<player_name>', methods=['GET'])
def get_location():
    pass
    # useless code v2
    # random changes