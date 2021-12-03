import asyncio
import logging
import random
import time
from typing import List, Optional

from sqlalchemy.orm.session import sessionmaker

from api.database.database import Engine, get_sessionmaker, playerdata, playerdata_engine
from api.database.functions import (batch_function, execute_sql, verify_token)
from api.database.models import Player as dbPlayer
from api.database.models import playerHiscoreData
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy.sql.expression import update, insert

logger = logging.getLogger(__name__)
router = APIRouter()

class hiscore(BaseModel):
    Player_id: int
    total: int
    attack: int
    defence: int
    strength: int
    hitpoints: int
    ranged: int
    prayer: int
    magic: int
    cooking: int
    woodcutting: int
    fletching: int
    fishing: int
    firemaking: int
    crafting: int
    smithing: int
    mining: int
    herblore: int
    agility: int
    thieving: int
    slayer: int
    farming: int
    runecraft: int
    hunter: int
    construction: int
    league: int
    bounty_hunter_hunter: int
    bounty_hunter_rogue: int
    cs_all: int
    cs_beginner: int
    cs_easy: int
    cs_medium: int
    cs_hard: int
    cs_elite: int
    cs_master: int
    lms_rank: int
    soul_wars_zeal: int
    abyssal_sire: int
    alchemical_hydra: int
    barrows_chests: int
    bryophyta: int
    callisto: int
    cerberus: int
    chambers_of_xeric: int
    chambers_of_xeric_challenge_mode: int
    chaos_elemental: int
    chaos_fanatic: int
    commander_zilyana: int
    corporeal_beast: int
    crazy_archaeologist: int
    dagannoth_prime: int
    dagannoth_rex: int
    dagannoth_supreme: int
    deranged_archaeologist: int
    general_graardor: int
    giant_mole: int
    grotesque_guardians: int
    hespori: int
    kalphite_queen: int
    king_black_dragon: int
    kraken: int
    kreearra: int
    kril_tsutsaroth: int
    mimic: int
    nightmare: int
    obor: int
    sarachnis: int
    scorpia: int
    skotizo: int
    tempoross:int
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    theatre_of_blood_hard: int
    thermonuclear_smoke_devil: int
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int

class Player(BaseModel):
    id: int
    name: Optional[str]
    possible_ban: Optional[bool]
    confirmed_ban: Optional[bool]
    confirmed_player: Optional[bool]
    label_id: Optional[int]
    label_jagex: Optional[int]

class scraper(BaseModel):
    hiscores: Optional[hiscore]
    player: Player

async def sql_get_players_to_scrape(page=1, amount=100_000):
    sql = 'select * from playersToScrape WHERE 1 ORDER BY RAND()'
    data = await execute_sql(sql, page=page, row_count=amount)
    return data.rows2dict()

@router.get("/scraper/players/{page}/{amount}/{token}", tags=["scraper"])
async def get_players_to_scrape(token, page:int=1, amount:int=100_000):
    await verify_token(token, verifcation='ban')
    return await sql_get_players_to_scrape(page=page, amount=amount)

async def handle_lock(function, data):
    sleep = random.uniform(1,5.1)
    logger.debug(f'{function.__name__=} Lock wait timeout exceeded, {sleep=}')
    await asyncio.sleep(sleep)
    await function(data)


async def sqla_update_player(players):
    engine = Engine()
    Session = engine.get_sessionmaker()
    logger.debug(f'update players: {len(players)=}')

    async with Session() as session:
        try:
            for player in players:
                player_id = player.get('id')
                sql = update(dbPlayer).values(player).where(dbPlayer.id==player_id)
                await session.execute(sql, player)
        except (OperationalError) as e:
            await handle_lock(sqla_update_player, players)

    await engine.engine.dispose()
    return

async def sqla_insert_hiscore(hiscores:List):
    engine = Engine()
    Session = engine.get_sessionmaker()
    logger.debug(f'insert hiscores: {len(hiscores)=}')

    sql = insert(playerHiscoreData).prefix_with('ignore')
    
    async with Session() as session:
        try:
            await session.execute(sql, hiscores)
            await session.commit()
        except (OperationalError) as e:
            await handle_lock(sqla_insert_hiscore, hiscores)
    await engine.engine.dispose()
    return

async def sample():
    # a sessionmaker(), also in the same scope as the engine
    Session = playerdata.session

    # we can now construct a Session() without needing to pass the
    # engine each time
    with Session() as session:
        session.execute()
        session.commit()
    # closes the session

@router.post("/scraper/hiscores/{token}", tags=["scraper"])
async def post_hiscores_to_db(token, data: List[scraper]):
    await verify_token(token, verifcation='ban')

    # get all players & all hiscores
    data = [d.dict() for d in data]
    players, hiscores = [], []

    for d in data:
        player_dict = d['player']
        hiscore_dict = d['hiscores']

        # add extra data
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        player_dict['updated_at'] = time_now
        
        players.append(player_dict)

        if hiscore_dict:
            hiscores.append(hiscore_dict)
    
    # batchwise insert & update
    await batch_function(sqla_insert_hiscore, hiscores, batch_size=10)
    await batch_function(sqla_update_player, players, batch_size=10)
    return {'ok':'ok'}
    
