from flask import Blueprint

player = Blueprint('player', __name__, template_folder='templates')

#TODO: verify token, see auth.py

@player.route('<version>/player/', methods=['GET'])
def get_player(version=None):
    pass

@player.route('<version>/player/', methods=['POST'])
def update_player(version=None):
    pass