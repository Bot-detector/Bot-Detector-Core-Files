import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from flask_cors import CORS
import sqlalchemy

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')

# create flask app
app = Flask(__name__)

# config flask app
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = sql_uri
# app.config['SQLALCHEMY_MAX_OVERFLOW'] = 2000: 
app.config['CORS_HEADERS'] = 'Content-Type'



# create database connection
db = SQLAlchemy(app)
db.session = db.create_scoped_session()

db_engines = {
   "playerdata": sqlalchemy.create_engine(sql_uri, poolclass=sqlalchemy.pool.NullPool),
   "discord": sqlalchemy.create_engine(discord_sql_uri, poolclass=sqlalchemy.pool.NullPool)
}
Session = sqlalchemy.orm.sessionmaker
db_sessions = {
   "playerdata": sqlalchemy.orm.sessionmaker(bind=db_engines['playerdata']),
   "discord": sqlalchemy.orm.sessionmaker(bind=db_engines['discord'])
}




# some cors stuf?
#Allows requests from all origins to all routes.
CORS(app, resources={r"/.*": {"origins": "*"}})

# create apscheduler, backgroundscheduler

executors = {
   # 'default': ThreadPoolExecutor(max_workers=4),
   'default': ProcessPoolExecutor() # processpool
}

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
   sched = BackgroundScheduler(daemon=False, executors=executors)

# todo cleanup in refactor
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
   app,
   key_func=get_remote_address,
   default_limits=["60 per minute", "5 per second"],
   strategy='fixed-window-elastic-expiry'
)

@limiter.request_filter
def ip_whitelist():
   whitelist = [
      '127.0.0.1',
      '45.76.255.154'
   ]
   return request.remote_addr in whitelist