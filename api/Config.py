import warnings
import json
import logging
import os
import sys

# import logging_loki
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# load environment variables
load_dotenv(find_dotenv(), verbose=True)
sql_uri = os.environ.get('sql_uri')
discord_sql_uri = os.environ.get('discord_sql_uri')
proxy_http = os.environ.get('proxy_http')
proxy_https = os.environ.get('proxy_https')
graveyard_webhook_url = os.environ.get('graveyard_webhook')
dev_mode = os.environ.get('dev_mode')
token = os.environ.get('token')

loki_url = os.environ.get('loki_url')
loki_user = os.environ.get('loki_user')
loki_pw = os.environ.get('loki_pw')

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
formatter = logging.Formatter(json.dumps(
    {
        'ts': '%(asctime)s',
        'name': '%(name)s',
        'function': '%(funcName)s',
        'level':'%(levelname)s',
        'msg': json.dumps('%(message)s')
    }
))


file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

handlers = [
    file_handler,
    stream_handler
]


# if not loki_url is None:
#     loki_handler = logging_loki.LokiQueueHandler(
#         Queue(-1),
#         url=f"{loki_url}",  # https://my-loki-instance/loki/api/v1/push
#         tags={"application": "api"},
#         auth=(f"{loki_user}", f"{loki_pw}"),
#         version="1",
#     )
#     loki_handler.setFormatter(formatter)
#     handlers.append(loki_handler)

logging.basicConfig(level=logging.DEBUG, handlers=handlers)

# set imported loggers to warning
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("aiomysql").setLevel(logging.ERROR)

logging.getLogger("uvicorn.error").propagate = False


# https://github.com/aio-libs/aiomysql/issues/103

# Suppress warnings only for aiomysql, all other modules can send warnings
warnings.filterwarnings('ignore', module=r"aiomysql")
warnings.filterwarnings('ignore', module=r"asyncmy")
