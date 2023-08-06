import asyncio
from asyncio import Queue
from aiokafka import AIOKafkaProducer


class KafkaMessageProducer:
    def __init__(self, bootstrap_servers, producer_topic):
        self.bootstrap_servers = bootstrap_servers
        self.producer_topic = producer_topic
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            loop=asyncio.get_event_loop(),
            bootstrap_servers=self.bootstrap_servers,
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def produce_message(self, message):
        try:
            await self.producer.send(self.producer_topic, message.encode("utf-8"))
        except Exception as e:
            print(f"Error producing message: {e}")

    async def produce_messages_from_queue(self, producer_queue: Queue):
        while True:
            await self.start()
            try:
                async for message in producer_queue:
                    await self.produce_message(message)
                    producer_queue.task_done()
            finally:
                await self.stop()

            await asyncio.sleep(5)
