import requests
import random
import time
import datetime as dt
# handling rate limits and stuf
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures as cf
import json
import pandas as pd
import logging as lg
# custom
import Config
import SQL

lg.getLogger("requests").setLevel(lg.WARNING)
lg.getLogger("urllib3").setLevel(lg.WARNING)

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 OPR/72.0.3815.320",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 Edg/87.0.664.41",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.58",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 OPR/72.0.3815.186",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.56",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.61",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.284",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.68",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47",
    "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.126 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36/8mqQhSuL-09",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
]

skills = {
    "total": "",
    "Attack": "",
    "Defence": "",
    "Strength": "",
    "Hitpoints": "",
    "Ranged": "",
    "Prayer": "",
    "Magic": "",
    "Cooking": "",
    "Woodcutting": "",
    "Fletching": "",
    "Fishing": "",
    "Firemaking": "",
    "Crafting": "",
    "Smithing": "",
    "Mining": "",
    "Herblore": "",
    "Agility": "",
    "Thieving": "",
    "Slayer": "",
    "Farming": "",
    "Runecraft": "",
    "Hunter": "",
    "Construction": "",
}

minigames = {
    "league": "",
    "bounty_hunter_hunter": "",
    "bounty_hunter_rogue": "",
    "cs_all": "",
    "cs_beginner": "",
    "cs_easy": "",
    "cs_medium": "",
    "cs_hard": "",
    "cs_elite": "",
    "cs_master": "",
    "lms_rank": "",
    "soul_wars_zeal": "",
    "abyssal_sire": "",
    "alchemical_hydra": "",
    "barrows_chests": "",
    "bryophyta": "",
    "callisto": "",
    "cerberus": "",
    "chambers_of_xeric": "",
    "chambers_of_xeric_challenge_mode": "",
    "chaos_elemental": "",
    "chaos_fanatic": "",
    "commander_zilyana": "",
    "corporeal_beast": "",
    "crazy_archaeologist": "",
    "dagannoth_prime": "",
    "dagannoth_rex": "",
    "dagannoth_supreme": "",
    "deranged_archaeologist": "",
    "general_graardor": "",
    "giant_mole": "",
    "grotesque_guardians": "",
    "hespori": "",
    "kalphite_queen": "",
    "king_black_dragon": "",
    "kraken": "",
    "kreearra": "",
    "kril_tsutsaroth": "",
    "mimic": "",
    "nightmare": "",
    "obor": "",
    "sarachnis": "",
    "scorpia": "",
    "skotizo": "",
    "Tempoross":"",
    "the_gauntlet": "",
    "the_corrupted_gauntlet": "",
    "theatre_of_blood": "",
    "thermonuclear_smoke_devil": "",
    "tzkal_zuk": "",
    "tztok_jad": "",
    "venenatis": "",
    "vetion": "",
    "vorkath": "",
    "wintertodt": "",
    "zalcano": "",
    "zulrah": ""
}


def logging(f):
    def wrapper(*args, **kwargs):
        start = dt.datetime.now()
        result = f(*args, **kwargs)
        end = dt.datetime.now()
        print(f'    {f.__name__} took: {end - start}')
        return result
    return wrapper


def make_web_call(URL, user_agent_list, debug=False):
    # Pick a random user agent
    user_agent = random.choice(user_agent_list)
    # Set the headers
    headers = {'User-Agent': user_agent}

    # {backoff factor} * (2 ** ({number of total retries} - 1)) seconds between retries
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    proxies = {
        'http': Config.proxy_http,
        'https': Config.proxy_https
    }
    # print(proxies)
    # Make the request

    response = http.get(URL, headers=headers, proxies=proxies)
    if response.status_code == 404:
        # player is banned, handled in mystasks

        return None
    else:
        response.raise_for_status()

    if debug:
        print(f'Requesting: {URL}')
        print(f'Response: Status code: {response.status_code}, response length: {len(response.text)}')
    return response


# @logging
def parse_highscores(data):
    # get list of keys from dict
    skills_keys = list(skills.keys())
    minigames_keys = list(minigames.keys())
    # data is huge array
    for index, row in enumerate(data):
        if index < len(skills):
            # skills row [rank, lvl, xp]
            skills[skills_keys[index]] = row.split(',')[2]
        else:
            index = index - (len(skills))
            # skills row [rank, Score]
            minigames[minigames_keys[index]] = row.split(',')[1]
    return skills, minigames


# @logging
def get_data(player_name):
    url = f'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={player_name}'
    # make a webcall
    data = make_web_call(url, user_agent_list)

    # if webcall returns nothing then signal player is banned
    if data is None:
        return None

    # splitlines will return an array
    data = data.text.splitlines()
    return data


'''
    old
'''
def mytasks(player_name):
    # get data
    data = get_data(player_name)

    # get player if return is none, the player does not exist
    player = SQL.get_player(player_name)
    
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

    # update the player so updated at is recent
    SQL.update_player(player.id, possible_ban=0, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, debug=False)

    # insert in hiscore data
    SQL.insert_highscore(player_id=player.id, skills=skills, minigames=minigames)

    return skills, minigames

# @logging
def main(player_names):
    for player_name in player_names:
        Config.sched.add_job(lambda: mytasks(player_name), replace_existing=False, name='hiscore')

'''
    end old
'''
# @logging
def my_sql_task(data, player_name, has_return=False):
    # get player if return is none, the player does not exist
    player = SQL.get_player(player_name)
    
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

    # update the player so updated at is recent
    SQL.update_player(player.id, possible_ban=0, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, debug=False)

    # insert in hiscore data
    SQL.insert_highscore(player_id=player.id, skills=skills, minigames=minigames)

    if has_return:
        return SQL.get_highscores_data_oneplayer(player_id=player.id)
    

def multi_thread(tasks):
    # multi thread the requesting of data
    lg.debug(f'     Starting multithread: {dt.datetime.now()}')
    print(f'     Starting multithread: {dt.datetime.now()}')
    mt_tasks = []
    for task in tasks:
        mt_tasks.append(([task]))

    i = 0
    with cf.ThreadPoolExecutor() as executor:

        futures = {executor.submit(get_data, task[0]): task[0] for task in mt_tasks}
        start = dt.datetime.now()
        for future in cf.as_completed(futures):
            i += 1
            player_name = futures[future]

            data = future.result()
            
            Config.sched.add_job(lambda: my_sql_task(data=data, player_name=player_name), max_instances=1_000_000, misfire_grace_time=60)
            if i % 100 == 0:
                end = dt.datetime.now()
                t = end - start
                lg.debug(f'     hiscores scraped: {100}, took: {t}, {dt.datetime.now()}')
                print(f'     hiscores scraped: {100}, took: {t}, {dt.datetime.now()}')
                start = dt.datetime.now()


def get_players():
    # get data
    data = SQL.get_players_to_scrape()
    if len(data) == 0:
        print('no players to scrape')
        return []

    df = pd.DataFrame(data)

    player_names = json.loads(df.to_json(orient='records'))
    #player_names = response.json()

    # filter data, to today
    interval_in_seconds = 24*60*60
    today = time.time()
    offset = (today % interval_in_seconds)
    rounded = today - offset
    today = rounded*1000

    # print(datetime.fromtimestamp(rounded), today)

    p_names = []
    for player in player_names:

        p_updated = player['updated_at']

        if p_updated is None:
            p_updated = 0

        # skip if player is banned
        if not (player['possible_ban'] == 0):
            continue

        # skip if player is banned
        if not (player['confirmed_ban'] == 0):
            continue

        # skip if we already updated the player
        if p_updated > today:
            continue

        # append player to player name list
        p_names.append(player['name'])

    print('players to scan:', len(p_names))
    return p_names


def run_hiscore():
    lg.debug(f'     Starting hiscore Scraper: {dt.datetime.now()}')
    print(f'     Starting hiscore Scraper: {dt.datetime.now()}')
    total = 0
    batch_size = 500
    refresh_factor = 2

    refresh_rate = batch_size * refresh_factor
    
    mt = True
    # endless loops
    while True:
        
        if total % refresh_rate == 0:
            player_names = get_players()

        # if batch size is empty
        if len(player_names) == 0:
            break

        # if total players is less then batch size
        if batch_size > len(player_names):
            end = True
        else:
            end = False

        if not (end):
            # start + batch_size can maximum be the length of players
            n_players = len(player_names) - batch_size
            # take a random starting point
            start = random.randint(0, n_players)
            # endpoint is start + batchsize
            end = start + batch_size
            # batch to scrape
            scrape_list = player_names[start:end]
        else:
            start, end = 0, 0
            scrape_list = player_names

        lg.debug(f'hiscore scraper status: TODO:{len(player_names)}, DONE:{total}, batch: start: {start}, end: {end}, date: {dt.datetime.now()}')
        print(f'hiscore scraper status: TODO: {len(player_names)}, DONE: {total}, batch: start: {start}, end: {end}, date: {dt.datetime.now()}')
        # get hiscores of all the players in batch
        if mt:
            multi_thread(scrape_list)
        else:
            main(scrape_list)
        total += len(scrape_list)

        # remove scraped players from our list of players
        player_names = [
            player for player in player_names if player not in scrape_list]


def scrape_one(player_name):
    data = get_data(player_name)
    return my_sql_task(data, player_name)

if __name__ == '__main__':
    run_hiscore()