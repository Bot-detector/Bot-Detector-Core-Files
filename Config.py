import logging
import os

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')
flask_port = os.environ.get('flask_port')
graveyard_webhook_url = os.environ.get('graveyard_webhook')

# TODO: BUG
# it does not like the bool()
try:
    dev_mode = os.environ.get('dev_mode')
except Exception as e:
    print(e)
    logging.debug(e)
    dev_mode=1

# create application
app = FastAPI()

# create databas engine
engine = create_engine(sql_uri, poolclass=NullPool)
discord_engine = create_engine(discord_sql_uri, poolclass=NullPool)

# setup logging
logging.FileHandler(filename="error.log", mode='a')
logging.basicConfig(filename='error.log', level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger('flask_cors').setLevel(logging.WARNING)

# for machine learning
n_pca=2
use_pca=False
