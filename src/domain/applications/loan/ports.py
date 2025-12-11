from abc import abstractmethod

from src.domain.ports import BaseRepository
from .entity import LoanApplication


class LoanApplicationRepository(BaseRepository[LoanApplication]):

    @abstractmethod
    async def get_by_applicant_id(self, applicant_id: str) -> LoanApplication | None:
        pass
