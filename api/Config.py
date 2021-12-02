import logging
import os
import sys

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')
graveyard_webhook_url = os.environ.get('graveyard_webhook')
dev_mode = os.environ.get('dev_mode')
token = os.environ.get('token')

# create application
app = FastAPI()

# setup logging
file_handler = logging.FileHandler(filename="logs/error.log", mode='a')
stream_handler = logging.StreamHandler(sys.stdout)
# # log formatting
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

handlers = [
    file_handler,
    stream_handler
]

logging.basicConfig(level=logging.DEBUG, handlers=handlers)

# set imported loggers to warning
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("aiomysql").setLevel(logging.ERROR)

logging.getLogger("uvicorn.error").propagate = False

# for machine learning
n_pca=2
use_pca=False

sched = AsyncIOScheduler()
sched.start()

bsched = BackgroundScheduler()
bsched.start()