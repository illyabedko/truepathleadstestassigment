import pytest

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus
from src.domain.applications.loan.processor import LoanApplicationProcessor, LoanProcessingRules
from src.domain.exceptions import ValidationError


class TestLoanApplicationProcessor:

    def test_validate_valid_application(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
        )

        processor.validate(app)  # Should not raise

    def test_validate_empty_applicant_id(self, processor):
        app = LoanApplication(
            applicant_id="",
            amount=10000,
            term_months=12,
        )

        with pytest.raises(ValidationError) as exc:
            processor.validate(app)

        assert exc.value.field == "applicant_id"

    def test_validate_negative_amount(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=-100,
            term_months=12,
        )

        with pytest.raises(ValidationError) as exc:
            processor.validate(app)

        assert exc.value.field == "amount"

    def test_validate_term_out_of_range(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=100,
        )

        with pytest.raises(ValidationError) as exc:
            processor.validate(app)

        assert exc.value.field == "term_months"

    def test_determine_status_approved(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,  # Below threshold
            term_months=12,
        )

        status = processor.determine_status(app)

        assert status == LoanApplicationStatus.APPROVED

    def test_determine_status_rejected(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=100000,  # Above threshold
            term_months=12,
        )

        status = processor.determine_status(app)

        assert status == LoanApplicationStatus.REJECTED

    def test_process_approved(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
        )

        result = processor.process(app)

        assert result.status == LoanApplicationStatus.APPROVED
        assert result.processed_at is not None

    def test_process_rejected_validation(self, processor):
        app = LoanApplication(
            applicant_id="user_123",
            amount=-100,
            term_months=12,
        )

        result = processor.process(app)

        assert result.status == LoanApplicationStatus.REJECTED
        assert result.rejection_reason is not None
