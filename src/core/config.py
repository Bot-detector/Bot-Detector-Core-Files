import json
import logging
import os
import sys
import warnings

# import logging_loki
from dotenv import find_dotenv, load_dotenv

# load environment variables
load_dotenv(find_dotenv(), verbose=True)

sql_uri = os.environ.get("sql_uri")
discord_sql_uri = os.environ.get("discord_sql_uri")
token = os.environ.get("token")
kafka_url = os.environ.get("kafka_url", "127.0.0.1:9094")
env = os.environ.get("env", "DEV")