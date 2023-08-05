import asyncio
import logging
import time
from asyncio import Queue

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import CommitFailedError

from src.core import config
from src.kafka.abc import AbstractConsumer, AbstractMP

logger = logging.getLogger(__name__)


class Kafka:
    def __init__(
        self,
        name: str,
        message_processor: AbstractMP,
        message_consumer: AbstractConsumer,
        topics: list,
        group_id: str,
        batch_size: int = 100,
    ) -> None:
        # Initialize the Kafka instance with the provided parameters.
        self.message_processor = message_processor
        self.message_consumer = message_consumer
        self.message_queue = Queue(maxsize=batch_size * 4)
        self.batch_size = batch_size
        self.name = name
        self.group_id = group_id
        self.topics: list = topics

    async def initialize(self):
        # Log the initialization process.
        logger.info(f"{self.name} - initializing")

        # Create an instance of AIOKafkaConsumer with specific configurations.
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=config.kafka_url,
            group_id=self.group_id,
            max_poll_interval_ms=60_000,
            session_timeout_ms=60_000,
            heartbeat_interval_ms=1_000,
            enable_auto_commit=False,
        )

        # Subscribe the consumer to the provided list of topics.
        self.consumer.subscribe(topics=self.topics)
        await self.consumer.start()
        return

    async def destroy(self):
        # Perform cleanup tasks when destroying the Kafka instance.
        pass

    async def run(self):
        logger.debug(f"running {self.name}")
        try:
            # Run both tasks concurrently using asyncio.gather
            await asyncio.gather(self.process_rows(), self.get_rows_from_kafka())
        except CommitFailedError as commit_error:
            logger.error(f"CommitFailedError: {str(commit_error)}")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            # After handling exceptions, continue running the loop
            await self.run()

    async def process_rows(self):
        # Process Kafka rows from the message queue.
        logger.info(f"{self.name} - start processing rows")
        last_send_time = int(time.time())
        batch = []
        while True:
            message: dict = await self.message_queue.get()
            batch.append(message)
            delta_send_time = int(time.time()) - last_send_time
            delta_send_time = delta_send_time if delta_send_time != 0 else 1

            if not batch:
                await asyncio.sleep(1)
                continue

            if len(batch) > self.batch_size or delta_send_time > 60:
                await self.message_consumer.process_batch(batch)
                last_send_time = int(time.time())
                qsize = self.message_queue.qsize()

                logger.info(
                    f"{self.name} - {qsize=} - {len(batch)/delta_send_time:.2f} it/s"
                )
                batch = []

            self.message_queue.task_done()
            await asyncio.sleep(0.01)

    async def get_rows_from_kafka(self):
        # Consume rows from Kafka and add them to the message queue.
        logger.info(f"{self.name} - start consuming rows from kafka")
        try:
            async for message in self.consumer:
                message = message.value.decode()
                message = await self.message_processor.process_message(message)
                await self.message_queue.put(message)
                await self.consumer.commit()
        except Exception as e:
            logger.error(f"Error in asynchronous tasks: {e}")
        finally:
            logger.warning(f"{self.name} - stopping consumer")
            await self.consumer.stop()
