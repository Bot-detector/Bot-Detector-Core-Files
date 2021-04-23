
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import random
import pandas as pd
import datetime as dt
import logging as lg
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures as cf
import traceback
# custom
import Config
import SQL
from scraper import extra_data as ed

lg.getLogger("requests").setLevel(lg.WARNING)
lg.getLogger("urllib3").setLevel(lg.WARNING)

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
        print(f'Requesting: {URL}')
        print(f'Response: Status code: {response.status_code}, response length: {len(response.text)}')
    return response

def get_data(player_name):
    url = f'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={player_name}'
    # make a webcall
    data = make_web_call(url, ed.user_agent_list)

    # if webcall returns nothing then signal player is banned
    if data is None:
        return None

    # splitlines will return an array
    data = data.text.splitlines()
    return data

def parse_highscores(data):
    skills = ed.skills
    minigames = ed.minigames
    # get list of keys from dict
    skills_keys = list(skills.keys())
    minigames_keys = list(minigames.keys())
    # data is huge array
    for index, row in enumerate(data):
        if index < len(skills):
            # skills row [rank, lvl, xp]
            skills[skills_keys[index]] = int(row.split(',')[2])
        else:
            index = index - (len(skills))
            # skills row [rank, Score]
            minigames[minigames_keys[index]] = int(row.split(',')[1])

    # fix total == 0
    if skills['total'] <= 0:
        skills_values = skills.values()
        skills_values = list(map(int, skills_values[1:]))
        skills_values = [item for item in skills_values if item > 0]
        skills['total'] == sum(skills_values)
        
    return skills, minigames
    
def my_sql_task(data, player_name, has_return=False):
    # get player if return is none, the player does not exist
    player = SQL.get_player(player_name)
    
    # if the player does not exist create the player
    if player is None:
        player = SQL.insert_player(player_name)

    # player variables
    cb = player.confirmed_ban
    cp = player.confirmed_player
    lbl = player.label_id

    # if hiscore data is none, then player is banned
    if data is None:
        SQL.update_player(player.id, possible_ban=1, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, debug=False)
        return None, None

    # else we parse the hiscore data
    skills, minigames = parse_highscores(data)

    # calculate total
    total = -1
    skills_list = list(map(int, skills.values()))
    minigames_list = list(map(int, minigames.values()))
    total = sum(skills_list) + sum(minigames_list)


    if total <= 0:
        SQL.update_player(player.id, possible_ban=0, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, debug=False)
        return None, None

    # insert in hiscore data
    SQL.insert_highscore(player_id=player.id, skills=skills, minigames=minigames)
    # update the player so updated at is recent
    SQL.update_player(player.id, possible_ban=0, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, debug=False)
    

    if has_return:
        return SQL.get_highscores_data_oneplayer(player_id=player.id)

def mytempfunction(player_name):
    data = get_data(player_name)
    _,_ = my_sql_task(data=data, player_name=player_name)
    return 1

def multi_thread(players):
    # create a list of tasks to multithread
    tasks = []
    for player in players:
        tasks.append(([player]))

    # multithreaded executor
    with cf.ProcessPoolExecutor() as executor:
        try:
            # submit each task to be executed
            futures = {executor.submit(mytempfunction, task[0]): task[0] for task in tasks} # get_data

            # get start time
            start = dt.datetime.now()
            for i, future in enumerate(cf.as_completed(futures)):
                # player_name = futures[future]
                # _ = future.result()
                # my_sql_task(data=data, player_name=player_name) # moved this to mytempfunction

                # some logging
                if i % 100 == 0:
                    end = dt.datetime.now()
                    t = end - start
                    lg.debug(f'     hiscores scraped: {100}, took: {t}, {dt.datetime.now()}')
                    print(f'     hiscores scraped: {100}, took: {t}, {dt.datetime.now()}')
                    start = dt.datetime.now()

        except Exception as e:
            print(f'Multithreading error: {e}')
            lg.debug(f'Multithreading error: {e}')
            lg.debug(traceback.print_exc())



def run_scraper():
    lg.debug(f'     Starting hiscore scraper: {dt.datetime.now()}')
    print(f'     Starting hiscore scraper: {dt.datetime.now()}')

    # get palyers to scrape
    data = SQL.get_players_to_scrape()

    # check if there are any players to scrape
    if len(data) == 0:
        print('no players to scrape')
        return []

    # array of named tuple to dataframe
    df = pd.DataFrame(data)

    # remove all possible banned
    # mask = ~(df['possible_ban'] == 1)
    # df = df[mask]

    # create array of players (names)
    players = df['name'].to_list()

    # define selections size
    n = 1000
    if n > len(players):
        n = len(players)

    # get a random sample from players with selection size
    players = random.sample(players, n)

    # multi thread scrape players
    multi_thread(players)


def scrape_one(player_name):
    data = get_data(player_name)
    return my_sql_task(data, player_name, has_return=True)


if __name__ == '__main__':
    run_scraper()
    