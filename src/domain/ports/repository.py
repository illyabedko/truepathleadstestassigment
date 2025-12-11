from abc import ABC, abstractmethod
from uuid import UUID


class BaseRepository[T](ABC):

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        pass

