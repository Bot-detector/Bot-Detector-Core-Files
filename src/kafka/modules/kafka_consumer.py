import asyncio
import json
from asyncio import Queue

from aiokafka import AIOKafkaConsumer
import logging

logger = logging.getLogger(__name__)


class KafkaMessageConsumer:
    def __init__(
        self, bootstrap_servers, consumer_topic, group_id, message_queue: Queue
    ):
        self.bootstrap_servers = bootstrap_servers
        self.consumer_topic = consumer_topic
        self.group_id = group_id
        self.message_queue = message_queue
        self.consumer = None

    async def start(self):
        logger.info("starting")
        self.consumer = AIOKafkaConsumer(
            self.consumer_topic,
            group_id=self.group_id,
            loop=asyncio.get_event_loop(),
            bootstrap_servers=self.bootstrap_servers,
        )
        await self.consumer.start()

    async def stop(self):
        logger.info("stopping")
        if self.consumer:
            await self.consumer.stop()

    async def consume_messages(self):
        logger.info("start consuming messages")
        try:
            async for message in self.consumer:
                message = message.value.decode("utf-8")
                message = json.loads(message)
                await self.message_queue.put(message)
        except Exception as e:
            print(f"Error consuming message: {e}")

    async def consume_messages_continuously(self):
        while True:
            await self.start()
            try:
                await self.consume_messages()
            finally:
                await self.stop()

            await asyncio.sleep(5)
