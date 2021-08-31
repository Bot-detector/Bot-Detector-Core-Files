import logging
import os
import sys
from multiprocessing import Queue

import logging_loki
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
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

# create application
app = FastAPI()

# setup logging
loki_handler = logging_loki.LokiQueueHandler(
    Queue(-1),
    url="http://loki:3100/loki/api/v1/push", 
    tags={"service": "scraper_continuous"},
)

if dev_mode == 0:
    logging.getLogger().addHandler(loki_handler)

logging.FileHandler(filename="error.log", mode='a')
logging.basicConfig(filename='error.log', level=logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger('flask_cors').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# for machine learning
n_pca=2
use_pca=False


executors = {
    # 'default': ThreadPoolExecutor(max_workers=4),
    'default': ProcessPoolExecutor()  # processpool
}
# scheduler
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    sched = BackgroundScheduler(daemon=False, executors=executors)