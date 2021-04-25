import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import random
import concurrent.futures as cf
import datetime as dt
import pandas as pd
import traceback
# custom
import Config
import SQL
import scraper.extra_data as ed

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

    response.raise_for_status()

    if debug:
        Config.debug(f'Requesting: {URL}')
        Config.debug(f'Response: Status code: {response.status_code}, response length: {len(response.text)}')
    return response

def check_player(player):
    player_name = player['name']
    # make web call
    url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player_name}'
    data = make_web_call(url, ed.user_agent_list, debug=False)
    data = data.json()

    # if no error, player exists
    if not('error' in data):
        return 'Real_Player'

    pb = player["possible_ban"]
    cb = player["confirmed_ban"]
    cp = player["confirmed_player"]
    lbl = player["label_id"]

    # this we don't know (unbanned?)
    if data['error'] == 'NO_PROFILE':
        if player["prediction"] == 'Real_Player':
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=1, debug=False)
        else:
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=1, confirmed_player=cp, label_id=lbl, label_jagex=1, debug=False)
        return data['error']

    # this is a bot
    if data['error'] == 'NOT_A_MEMBER':
        if player["prediction"] == 'Real_Player':
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=2, debug=False)
        else:
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=1, confirmed_player=cp, label_id=lbl, label_jagex=2, debug=False)
        return data['error']

    # unkown
    if data['error'] == 'PRIVATE_PROFILE':
        SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=3, debug=False)
        return data['error']

def main():
    players = SQL.get_possible_ban_predicted()
    Config.debug(len(players))
    tasks = []
    for player in players:
        player = dict(player._asdict())
        tasks.append(([player]))

    del players # memory optimalisation
    with cf.ProcessPoolExecutor() as executor:
        # submit each task to be executed
        # {function: param, ...}
        futures = {executor.submit(check_player, task[0]): task[0] for task in tasks}  # get_data
        # get start time
        start = dt.datetime.now()
        for i, future in enumerate(cf.as_completed(futures)):
            try:
                player= futures[future]
                result = future.result()
                Config.debug(f' scraped: {player["name"]} result: {result}')

                # some logging
                if i % 100 == 0 and not(i == 0):
                    end = dt.datetime.now()
                    t = end - start
                    Config.debug(f'     player Checked: {100}, total: {i}, took: {t}, {dt.datetime.now()}')
                    start = dt.datetime.now()

            except Exception as e:
                Config.debug(f'Multithreading error: {e}')
                Config.debug(traceback.print_exc())

if __name__ == '__main__':
    main()
