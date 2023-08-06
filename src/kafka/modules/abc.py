from abc import ABC, abstractmethod
from aiokafka import ConsumerRecord


class AbstractConsumer(ABC):
    @abstractmethod
    async def process_batch(self, batch: list[dict]):
        pass


class AbstractProcessor(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    async def process_batch(self) -> None:
        pass

    @abstractmethod
    async def process_message(self):
        pass
