from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.db.session import Base
from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus


class LoanApplicationModel(Base):

    __tablename__ = "loan_applications"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    applicant_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)

    def to_entity(self) -> LoanApplication:
        return LoanApplication(
            id=self.id,
            applicant_id=self.applicant_id,
            amount=self.amount,
            term_months=self.term_months,
            status=LoanApplicationStatus(self.status),
            created_at=self.created_at,
            processed_at=self.processed_at,
            rejection_reason=self.rejection_reason,
        )

    @classmethod
    def from_entity(cls, entity: LoanApplication) -> "LoanApplicationModel":
        return cls(
            id=entity.id,
            applicant_id=entity.applicant_id,
            amount=entity.amount,
            term_months=entity.term_months,
            status=entity.status.value,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
            rejection_reason=entity.rejection_reason,
        )

