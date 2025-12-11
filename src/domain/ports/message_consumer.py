from abc import ABC, abstractmethod
from typing import AsyncIterator


class MessageConsumer(ABC):

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    def messages(self) -> AsyncIterator[dict]:
        pass
