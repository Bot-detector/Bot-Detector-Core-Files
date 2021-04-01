import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

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

engine = create_engine(sql_uri)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

CORS(app, resources={r"/.*": {"origins": "*"}})

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
   sched = BackgroundScheduler(daemon=False)

