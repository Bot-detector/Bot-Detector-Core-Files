import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition

from src.app.repositories.highscore import PlayerHiscoreData as RepoHiscore
from src.app.repositories.player import Player as RepositoryPlayer
from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
from src.app.schemas.player import Player as SchemaPlayer
from src.database.models import playerHiscoreData as dbHiscore
from src.kafka.modules.kafka_consumer import KafkaMessageConsumer
from src.kafka.modules.kafka_producer import KafkaMessageProducer
from asyncio import Queue
import asyncio
import time
from src.core import config

logger = logging.getLogger(__name__)


class HighscoreProcessor:
    def __init__(self, batch_size: int = 100) -> None:
        self.repo_highscore = RepoHiscore()
        self.repo_player = RepositoryPlayer()
        self.message_queue = Queue(maxsize=batch_size * 2)
        self.batch = []

        self.batch_size = batch_size

    async def initialize(self):
        self.message_consumer = KafkaMessageConsumer(
            bootstrap_servers=config.kafka_url,
            consumer_topic="scraper",
            group_id="highscore-api",
            message_queue=self.message_queue,
        )

    async def start(self):
        logger.info("starting")
        while True:
            await self.initialize()
            try:
                await asyncio.gather(
                    self.message_consumer.consume_messages_continuously(),
                    self.process_messages(),
                )
            except Exception as error:
                logger.error(f"Error occured: {str(error)}")
            finally:
                await self.message_consumer.stop()
            await asyncio.sleep(5)

    async def process_messages(self):
        logger.info("start processing messages")
        last_send = int(time.time())
        while True:
            message: dict = await self.message_queue.get()

            self.batch.append(message)

            delta_send_time = int(time.time()) - last_send
            delta_send_time = delta_send_time if delta_send_time != 0 else 1

            qsize = self.message_queue.qsize()

            if len(self.batch) > self.batch_size or (
                delta_send_time > 60 and self.batch and qsize == 0
            ):
                last_send = int(time.time())
                await self.process_batch()

                logger.info(f"{qsize=} - {len(self.batch)/delta_send_time:.2f} it/s")
                self.batch = []

            self.message_queue.task_done()

    async def process_batch(self):
        # Lists to store processed highscores and players
        highscores: list[SchemaHiscore] = []
        players: list[SchemaPlayer] = []

        # Process each row of data containing 'hiscores' and 'player' information
        for row in self.batch:
            row: dict
            # Extract 'hiscores' and 'player' dictionaries from the row
            highscore = row.get("hiscores")
            player = row.get("player")

            # Create a SchemaPlayer object from the 'player' dictionary
            player = SchemaPlayer(**player)

            # Skip processing if the player's name is longer than 13 characters
            if len(player.name) > 13:
                continue

            # Append the player to the list of players
            players.append(player)

            # If 'hiscores' data exists, create a SchemaHiscore object and append it to the list
            if highscore:
                highscore = SchemaHiscore(**highscore)
                highscore.ts_date = highscore.timestamp.date()
                highscores.append(highscore)

        # Create new highscore records in the database using the repo_highscore
        # _ = await self.repo_highscore.create(data=highscores)
        if highscores:
            await self.repo_highscore.insert_if_not_exist(
                table=dbHiscore,
                schema=SchemaHiscore,
                unique_columns=["Player_id", "ts_date"],
                values=highscores,
            )
        if players:
            # Update player records in the database using the repo_player
            await self.repo_player.update(data=players)
        return
