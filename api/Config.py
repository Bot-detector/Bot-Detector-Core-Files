import logging
import os
import sys

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, background
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')
flask_port = os.environ.get('flask_port')
graveyard_webhook_url = os.environ.get('graveyard_webhook')
dev_mode = os.environ.get('dev_mode')
token = os.environ.get('token')

# create application
app = FastAPI()

# setup logging
logger = logging.getLogger()
#file_handler = logging.FileHandler(filename="logs/dev-error.log", mode='a')
stream_handler = logging.StreamHandler(sys.stdout)

#logging.basicConfig(filename='logs/dev-error.log', level=logging.DEBUG)

# log formatting
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add handler
#logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# set imported loggers to warning
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger('flask_cors').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

# for machine learning
n_pca=2
use_pca=False

sched = AsyncIOScheduler()
sched.start()

bsched = BackgroundScheduler()
bsched.start()