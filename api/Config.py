import logging
import os
import sys

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
token = os.environ.get('token')

# create application
app = FastAPI()

origins = [
    "http://osrsbotdetector.com/",
    "https://osrsbotdetector.com/",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# https://github.com/aio-libs/aiomysql/issues/103
import warnings
# Suppress warnings only for aiomysql, all other modules can send warnings
warnings.filterwarnings('ignore', module=r"aiomysql")
warnings.filterwarnings('ignore', module=r"asyncmy")