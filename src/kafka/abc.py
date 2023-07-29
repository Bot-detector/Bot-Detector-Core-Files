from abc import ABC, abstractmethod
from aiokafka import AIOKafkaConsumer, TopicPartition, ConsumerRecord


class AbstractConsumer(ABC):
    @abstractmethod
    async def process(self, data: list[dict]):
        pass


class AbstractMP(ABC):
    @abstractmethod
    async def parse_and_commit(
        self,
        consumer: AIOKafkaConsumer,
        msgs: dict[TopicPartition, list[ConsumerRecord]],
        batch: list,
        name: str,
    ) -> list:
        pass
