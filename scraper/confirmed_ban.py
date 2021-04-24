# NO_PROFILE = unbanned
# NOT_A_MEMBER = banned
# PRIVATE_PROFILE = Unable to figure out, check hiscore if it appears there
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import random
import pandas as pd
# custom
import Config
import SQL

def make_web_call(URL, user_agent_list, debug=False):
    # Pick a random user agent
    user_agent = random.choice(user_agent_list)
    # Set the headers
    headers = {'User-Agent': user_agent}

    # {backoff factor} * (2 ** ({number of total retries} - 1)) seconds between retries
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )

    # create adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    # define proxy
    proxies = {
        'http': Config.proxy_http,
        'https': Config.proxy_https
    }
    
    # Make the request
    response = http.get(URL, headers=headers, proxies=proxies)

    # if response is 404, this means player is banned or name is changed
    if response.status_code == 404:
        return None
    else:
        response.raise_for_status()

    if debug:
        Config.debug(f'Requesting: {URL}')
        Config.debug(f'Response: Status code: {response.status_code}, response length: {len(response.text)}')
    return response

url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player_name}'

players = SQL.get_possible_ban()
players = pd.DataFrame(players)