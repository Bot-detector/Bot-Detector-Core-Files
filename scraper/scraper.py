import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import SQL
import Config
from flask import Blueprint, jsonify, request
from mysite.tokens import verify_token

app_scraper = Blueprint('app_scraper', __name__)


@app_scraper.route("/scraper/players/<token>", methods=['GET'])
@app_scraper.route("/scraper/players/<start>/<amount>/<token>", methods=['GET']) # we could also work with arguments
def get_players_to_scrape(token, start=None, amount=None):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404

    data = SQL.get_players_to_scrape(start, amount)

    df = pd.DataFrame(data)
    output = df.to_dict('records')

    return jsonify(output)


@app_scraper.route("/scraper/hiscores/<token>", methods=['POST'])
def post_hiscores_to_db(token):
    if not (verify_token(token, verifcation='ban')):
        return "<h1>404</h1><p>Invalid token</p>", 404
    data = request.get_json()
    Config.debug(data)
    return jsonify({'OK':'OK'})
