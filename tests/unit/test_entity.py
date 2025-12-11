import pytest
from uuid import UUID

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus


class TestLoanApplication:

    def test_create_with_defaults(self):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
        )

        assert app.applicant_id == "user_123"
        assert app.amount == 10000
        assert app.term_months == 12
        assert app.status == LoanApplicationStatus.PENDING
        assert isinstance(app.id, UUID)
        assert app.rejection_reason is None

    def test_to_dict(self):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
        )

        data = app.to_dict()

        assert data["applicant_id"] == "user_123"
        assert data["amount"] == 10000
        assert data["term_months"] == 12
        assert data["status"] == "pending"
        assert "id" in data

    def test_from_dict(self):
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "applicant_id": "user_123",
            "amount": 10000,
            "term_months": 12,
            "status": "approved",
        }

        app = LoanApplication.from_dict(data)

        assert app.applicant_id == "user_123"
        assert app.amount == 10000
        assert app.status == LoanApplicationStatus.APPROVED

