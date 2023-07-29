import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition

from src.app.repositories.highscore import PlayerHiscoreData as RepoHiscore
from src.app.repositories.player import Player as RepositoryPlayer
from src.app.schemas.highscore import PlayerHiscoreData as SchemaHiscore
from src.app.schemas.player import Player as SchemaPlayer
from src.kafka.abc import AbstractConsumer, AbstractMP

logger = logging.getLogger(__name__)


class MessageProcessor(AbstractMP):
    def __init__(self):
        pass

    async def parse_and_commit(
        self,
        consumer: AIOKafkaConsumer,
        msgs: dict[TopicPartition, list[ConsumerRecord]],
        batch: list,
        name: str,
    ) -> list:
        # Loop through each topic and its associated messages in the received batch.
        for topic, messages in msgs.items():
            # Log information about the current processing status for the topic.
            logger.info(f"{name} - {topic=}, {len(messages)=}, {len(batch)=}")

            # Convert the messages from bytes to JSON and add them to the batch.
            data = [json.loads(msg.value.decode()) for msg in messages]
            batch.extend(data)

            # Commit the offset of the latest seen message in the topic to mark it as processed.
            msg: ConsumerRecord = messages[-1]
            tp = TopicPartition(msg.topic, msg.partition)
            await consumer.commit({tp: msg.offset + 1})

        # Return the updated batch after processing all topics.
        return batch


class HiscoreConsumer(AbstractConsumer):
    # Initialize the repositories for highscores and players
    repo_highscore = RepoHiscore()
    repo_player = RepositoryPlayer()

    async def process(self, data: list[dict[str, dict]]):
        # Lists to store processed highscores and players
        highscores: list[SchemaHiscore] = []
        players: list[SchemaPlayer] = []

        # Process each row of data containing 'hiscores' and 'player' information
        for row in data:
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
                highscores.append(highscore)

        # Create new highscore records in the database using the repo_highscore
        new_records = await self.repo_highscore.create(data=highscores)

        # Extract the Player IDs from the newly created highscore records
        player_ids = [r.Player_id for r in new_records]

        # Filter the list of players to include only those with matching Player IDs
        players = [p for p in players if p.id in player_ids]

        # Update player records in the database using the repo_player
        await self.repo_player.update(data=players)
        return
