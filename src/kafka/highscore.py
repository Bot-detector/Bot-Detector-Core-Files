import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer, TopicPartition

from src.app.repositories.highscore import (
    PlayerHiscoreData as RepositoryPlayerHiscoreData,
)
from src.app.repositories.player import Player as RepositoryPlayer

from src.app.schemas.highscore import PlayerHiscoreData as SchemaPlayerHiscoreData
from src.app.schemas.player import Player as SchemaPlayer
from src.core import config
import random
import time

logger = logging.getLogger(__name__)


async def procces_scraper_consumer(data: list[dict]):
    repo_highscore = RepositoryPlayerHiscoreData()
    repo_player = RepositoryPlayer()

    highscores = []
    players = []
    for row in data:
        highscore = row.get("hiscores")
        player = row.get("player")

        player = SchemaPlayer(**player)

        if len(player.name) > 13:
            continue

        players.append(player)

        if highscore:
            highscore = SchemaPlayerHiscoreData(**highscore)
            highscores.append(highscore)

    await repo_highscore.create(data=highscores)
    await repo_player.update(data=players)
    return


async def run_kafka_scraper_consumer():
    bootstrap_servers = config.kafka_url
    group_id = "highscore-api"
    sleep = 1
    batch = []
    send_time = time.time()

    HEARTHBEAT_INTERVAL = 30_000
    consumer = AIOKafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        max_poll_interval_ms=HEARTHBEAT_INTERVAL * 3,
        session_timeout_ms=HEARTHBEAT_INTERVAL * 3,  # 1 minute
        heartbeat_interval_ms=HEARTHBEAT_INTERVAL,  # 10 seconds
        enable_auto_commit=False,
    )

    consumer.subscribe(topics=["scraper"])
    await consumer.start()

    try:
        while True:
            msgs = await consumer.getmany(max_records=100)

            # capped exponential sleep
            if msgs == {}:
                logger.info("no messages, sleeping")
                await asyncio.sleep(sleep)
                sleep = sleep * 2 if sleep * 2 < 60 else 60
                continue

            # parsing all messages
            for topic, messages in msgs.items():
                logger.info(f"{topic=}, {len(messages)=}, {len(batch)=}")
                data: list[dict] = [json.loads(msg.value.decode()) for msg in messages]
                batch.extend(data)

                if len(batch) >= 100 or send_time + 60 < time.time():
                    await procces_scraper_consumer(batch)
                    batch = []
                    send_time = time.time()

                # commit the latest seen message
                msg = messages[-1]
                tp = TopicPartition(msg.topic, msg.partition)
                await consumer.commit({tp: msg.offset + 1})

            # reset sleep
            sleep = 1
    except Exception as e:
        logger.error(f"Caught Exception:\n {str(e)}")
        # Add a random sleep time between 100ms to 1000ms (adjust as needed).
        sleep_time_ms = random.randint(1000, 5000)
        await asyncio.sleep(sleep_time_ms / 1000)
        await run_kafka_scraper_consumer()
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_kafka_scraper_consumer())
