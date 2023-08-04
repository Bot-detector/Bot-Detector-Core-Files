import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition

from src.app.repositories.highscore import PlayerHiscoreData as RepoHiscore
from src.app.repositories.player import Player as RepositoryPlayer
from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
from src.app.schemas.player import Player as SchemaPlayer
from src.kafka.abc import AbstractConsumer, AbstractMP
from src.database.models import playerHiscoreData as dbHiscore

logger = logging.getLogger(__name__)


class MessageProcessor(AbstractMP):
    async def process_message(self, message: ConsumerRecord) -> dict:
        message = json.loads(message)
        return message


class HiscoreConsumer(AbstractConsumer):
    # Initialize the repositories for highscores and players
    repo_highscore = RepoHiscore()
    repo_player = RepositoryPlayer()

    async def process_batch(self, batch: list[dict]):
        # Lists to store processed highscores and players
        highscores: list[SchemaHiscore] = []
        players: list[SchemaPlayer] = []

        # Process each row of data containing 'hiscores' and 'player' information
        for row in batch:
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
