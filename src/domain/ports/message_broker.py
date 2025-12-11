from abc import ABC, abstractmethod


class MessageBroker(ABC):

    @abstractmethod
    async def publish(self, topic: str, message: dict, key: str | None = None) -> None:
        pass
