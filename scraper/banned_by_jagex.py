import os, sys

from discord_webhook.webhook import DiscordEmbed
from flask import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discord_webhook import DiscordWebhook
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import random
import concurrent.futures as cf
import datetime as dt
import pandas as pd
import traceback
import random
# custom
import Config
import SQL
import scraper.extra_data as ed

players_banned = []

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

    pb = player["possible_ban"]
    cb = player["confirmed_ban"]
    cp = player["confirmed_player"]
    lbl = player["label_id"]
    lbl_jgx = player["label_jagex"]

    new_ban = False

    # if no error, player exists
    if not('error' in data):
        SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=5, debug=False)
        return 'Real_Player', new_ban

    # this we don't know (unbanned?)
    if data['error'] == 'NO_PROFILE':
        SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=1, debug=False)
        return data['error'], new_ban

    # this is a bot
    if data['error'] == 'NOT_A_MEMBER':
        # confirmed ban should only be players that we predict as bot and jagex bans.
        if player["prediction"] == 'Real_Player':
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=2, debug=False)
        else:
            SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=1, confirmed_player=cp, label_id=lbl, label_jagex=2, debug=False)
            
        if not (lbl_jgx == 2):
            new_ban = True 
        
        return data['error'], new_ban

    # unkown
    if data['error'] in ('PRIVATE_PROFILE', 'PROFILE_PRIVATE') :
        SQL.update_player(player['id'], possible_ban=pb, confirmed_ban=cb, confirmed_player=cp, label_id=lbl, label_jagex=3, debug=False)
        return data['error'], new_ban

    return 'wtf', new_ban

def confirm_possible_ban():
    for _ in range(10):
        n = 1000
        players = SQL.get_possible_ban_predicted(amount=n)
        Config.debug(len(players))
        
        tasks = []
        for player in players:
            player = dict(player._asdict())
            tasks.append(([player]))

        del players # memory optimalisation

        players_banned = []

        with cf.ThreadPoolExecutor() as executor:
            # submit each task to be executed
            # {function: param, ...}
            futures = {executor.submit(check_player, task[0]): task[0] for task in tasks}  # get_data
            del tasks # memory optimalisation
            # get start time
            start = dt.datetime.now()
            

            for i, future in enumerate(cf.as_completed(futures)):
                try:
                    player= futures[future]
                    result, new_ban = future.result()

                    if new_ban:
                        players_banned.append(player["name"])

                    # some logging
                    if i % 100 == 0 and not(i == 0):
                        end = dt.datetime.now()
                        t = end - start
                        Config.debug(f'     player Checked: {100}, total: {i}, took: {t}, {dt.datetime.now()}')
                        start = dt.datetime.now()

                except Exception as e:
                    Config.debug(f'Multithreading error: {e}')
                    Config.debug(traceback.print_exc())

        fill_graveyard_plots(players_banned)

        del futures, future, player, result, start, end, t, i # memory optimalisation?

    return


#Sends an embed to the #bot-graveyard channel on our Discord server
def fill_graveyard_plots(players_banned):
    # if is empty list return
    if not players_banned:
        Config.debug(f'There is no data in {players_banned}')
        return
    
    webhook = DiscordWebhook(url=Config.graveyard_webhook_url)
    embed = DiscordEmbed(title="All Ye Bots Lose All Hope", color="000000")

    embed.set_timestamp()
    embed.add_embed_field(name="Newly Departed", value=f"{', '.join(players_banned)}")
    embed.set_thumbnail(url="https://i.imgur.com/pwtJVPj.gif")

    webhook.add_embed(embed=embed)
    webhook.execute()

    return 


if __name__ == '__main__':
    confirm_possible_ban()
