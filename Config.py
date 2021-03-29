import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from flask_cors import CORS

load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = sql_uri
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 2000
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

CORS(app, resources={r"/.*": {"origins": "*"}})

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
   sched = BackgroundScheduler(daemon=False, executors={'default': ProcessPoolExecutor(max_workers=1)})