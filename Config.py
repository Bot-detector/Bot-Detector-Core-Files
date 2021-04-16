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
app.config['CORS_HEADERS'] = 'Content-Type'

db_engines = {
   "playerdata":  sqlalchemy.create_engine(sql_uri,         poolclass=sqlalchemy.pool.NullPool),
   "discord":     sqlalchemy.create_engine(discord_sql_uri, poolclass=sqlalchemy.pool.NullPool)
}

Session = sqlalchemy.orm.sessionmaker

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

