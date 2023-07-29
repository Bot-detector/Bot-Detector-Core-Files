import asyncio
import logging
import random
import time
import traceback

from aiokafka import AIOKafkaConsumer

from src.core import config
from src.kafka.abc import AbstractConsumer, AbstractMP

logger = logging.getLogger(__name__)


class Kafka:
    def __init__(
        self,
        name: str,
        message_processor: AbstractMP,
        message_consumer: AbstractConsumer,
    ) -> None:
        self.message_processor = message_processor
        self.message_consumer = message_consumer
        self.name = name

    async def initialize(self, group_id: str, topics: list[str]):
        # Log the initialization process.
        logger.info(f"{self.name} - initializing")

        # Create an instance of AIOKafkaConsumer with specific configurations.
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=config.kafka_url,
            group_id=group_id,
            max_poll_interval_ms=60_000,
            session_timeout_ms=60_000,
            heartbeat_interval_ms=1_000,
            enable_auto_commit=False,
        )

        # Subscribe the consumer to the provided list of topics.
        self.consumer.subscribe(topics=topics)

        # Start the consumer.
        await self.consumer.start()
        return

    async def _handle_no_messages(self, sleep: int, delta: int = 0):
        # Log that there are no messages, and sleep for a specified duration.
        logger.info(f"{self.name} - no messages, sleeping {sleep}")
        await asyncio.sleep(sleep)
        return sleep + delta

    async def _process_batch(self, batch) -> list:
        now = time.time()
        # If the time since the last batch processing is less than 60 seconds, return the batch as is.
        # If the batch size is less than 100, return the batch as is.
        if not (self.send_time + 60 < now or len(batch) >= 100):
            return batch

        # If both conditions are met, process the batch using the message_consumer's process method.
        start_time = time.time()
        await self.message_consumer.process(batch)
        end_time = time.time()

        # Log the time taken for processing the batch.
        delta_time = end_time - start_time
        logger.info(
            f"Inserting: {len(batch)} took {delta_time:.2f} seconds, {len(batch)/delta_time:.2f} it/s,"
        )

        # Update the send_time with the end_time for the next batch processing.
        self.send_time = end_time
        return []

    async def run(self):
        # Log that the Kafka consumer is running.
        logger.info(f"{self.name} - running")

        # Initialize a list to hold the batch of messages.
        batch = []

        # Initialize the send_time to the current time.
        self.send_time = time.time()

        # Set the initial sleep duration to 2.9 seconds.
        sleep = 2.9

        try:
            while True:
                # Get a batch of messages from the consumer.
                msgs = await self.consumer.getmany(max_records=100)

                # If there are no messages in the batch, sleep for a specified duration and continue the loop.
                if not msgs:
                    sleep = await self._handle_no_messages(sleep, 0)
                    continue

                # Parse and commit the messages using the message_processor.
                batch = await self.message_processor.parse_and_commit(
                    consumer=self.consumer, msgs=msgs, batch=batch, name=self.name
                )

                # If the batch is empty after processing, continue the loop.
                if not batch:
                    continue

                # Process the batch.
                batch = await self._process_batch(batch)
        except Exception as e:
            # Log any exceptions caught during the consumer's execution.
            logger.error(f"Caught Exception:\n {str(e)}\n{traceback.format_exc()}")

            # Sleep for a random duration between 1 and 5 seconds before attempting to run again.
            sleep_time_ms = random.randint(1000, 5000)
            await asyncio.sleep(sleep_time_ms / 1000)

            # Restart the consumer by calling the run method again.
            await self.run()
        finally:
            # Stop the consumer when the consumer loop exits.
            await self.consumer.stop()
