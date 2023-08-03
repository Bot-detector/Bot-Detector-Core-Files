from abc import ABC, abstractmethod
from aiokafka import ConsumerRecord


class AbstractConsumer(ABC):
    @abstractmethod
    async def process_batch(self, batch: list[dict]):
        pass


class AbstractMP(ABC):
    @abstractmethod
    async def process_message(self, message: ConsumerRecord) -> dict:
        pass
