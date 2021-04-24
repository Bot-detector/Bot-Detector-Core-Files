import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import random
import concurrent.futures as cf
import datetime as dt
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

    # if response is 404, this means player is banned or name is changed
    if response.status_code == 404:
        return None
    else:
        response.raise_for_status()

    if debug:
        Config.debug(f'Requesting: {URL}')
        Config.debug(f'Response: Status code: {response.status_code}, response length: {len(response.text)}')
    return response

def check_player(player):
    player_name = player.name
    # make web call
    url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player_name}'
    data = make_web_call(url, ed.user_agent_list, debug=False)
    data = data.json()

    # if no error, player exists
    if not('error' in data):
        return


    # NO_PROFILE = unbanned
    # NOT_A_MEMBER = banned
    # PRIVATE_PROFILE = Unable to figure out, check hiscore if it appears there

    # check if player is banned
    if not(data['error'] == 'NOT_A_MEMBER'):
        return
    Config.debug(f'player: {player_name} is banned')

    if player.prediction == '':
        pass
    # SQL.update_player(player.id, possible_ban=1, confirmed_ban=1, confirmed_player=0, label_id=0, debug=False)



def main():
    players = SQL.get_possible_ban_predicted() 
    tasks = []
    for player in players:
        tasks.append(([player]))

    with cf.ProcessPoolExecutor() as executor:
        # submit each task to be executed
        futures = {executor.submit(check_player, task[0]): task[0] for task in tasks}  # get_data
        # get start time
        start = dt.datetime.now()
        for i, future in enumerate(cf.as_completed(futures)):
            player_name = futures[future]
            # Config.debug(f' scraped: {player_name}')
            # some logging
            if i % 100 == 0:
                end = dt.datetime.now()
                t = end - start
                Config.debug(f'     hiscores scraped: {100}, took: {t}, {dt.datetime.now()}')
                start = dt.datetime.now()
        



# players = pd.DataFrame(players)

if __name__ == '__main__':
    main()
