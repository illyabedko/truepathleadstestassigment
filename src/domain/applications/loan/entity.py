from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .value_objects import LoanApplicationStatus


@dataclass
class LoanApplication:

    applicant_id: str
    amount: float
    term_months: int
    id: UUID = field(default_factory=uuid4)
    status: LoanApplicationStatus = LoanApplicationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None
    rejection_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "applicant_id": self.applicant_id,
            "amount": self.amount,
            "term_months": self.term_months,
            "status": self.status.value if isinstance(self.status, LoanApplicationStatus) else self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "rejection_reason": self.rejection_reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LoanApplication":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        processed_at = data.get("processed_at")
        if isinstance(processed_at, str):
            processed_at = datetime.fromisoformat(processed_at)

        return cls(
            id=UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid4()),
            applicant_id=data["applicant_id"],
            amount=data["amount"],
            term_months=data["term_months"],
            status=LoanApplicationStatus(data["status"]) if data.get("status") else LoanApplicationStatus.PENDING,
            created_at=created_at or datetime.utcnow(),
            processed_at=processed_at,
            rejection_reason=data.get("rejection_reason"),
        )
