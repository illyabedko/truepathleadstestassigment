from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.ports import LoanApplicationRepository
from .model import LoanApplicationModel


class PostgresLoanApplicationRepository(LoanApplicationRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: LoanApplication) -> LoanApplication:
        existing = await self._session.get(LoanApplicationModel, entity.id)

        if existing:
            existing.applicant_id = entity.applicant_id
            existing.amount = entity.amount
            existing.term_months = entity.term_months
            existing.status = entity.status.value
            existing.processed_at = entity.processed_at
            existing.rejection_reason = entity.rejection_reason
            model = existing
        else:
            model = LoanApplicationModel.from_entity(entity)
            self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)

        return model.to_entity()

    async def get_by_id(self, entity_id: UUID) -> LoanApplication | None:
        model = await self._session.get(LoanApplicationModel, entity_id)
        return model.to_entity() if model else None

    async def get_by_applicant_id(self, applicant_id: str) -> LoanApplication | None:
        query = (
            select(LoanApplicationModel)
            .where(LoanApplicationModel.applicant_id == applicant_id)
            .order_by(desc(LoanApplicationModel.created_at))
            .limit(1)
        )

        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        return model.to_entity() if model else None

