import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = sql_uri
db = SQLAlchemy(app)

sched = BackgroundScheduler(daemon=True)