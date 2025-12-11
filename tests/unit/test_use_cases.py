import pytest
from unittest.mock import AsyncMock

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus
from src.domain.applications.loan.processor import LoanApplicationProcessor, LoanProcessingRules
from src.domain.applications.loan.use_cases import (
    SubmitApplicationUseCase,
    GetApplicationStatusUseCase,
    ProcessApplicationUseCase,
)
from src.domain.exceptions import ValidationError


class TestSubmitApplicationUseCase:

    @pytest.fixture
    def use_case(self, mock_message_broker, processor):
        return SubmitApplicationUseCase(
            message_broker=mock_message_broker,
            processor=processor,
            topic="loan-applications",
        )

    @pytest.mark.asyncio
    async def test_submit_valid_application(self, use_case, mock_message_broker):
        result = await use_case.execute(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
        )

        assert result.applicant_id == "user_123"
        assert result.status == LoanApplicationStatus.PENDING
        mock_message_broker.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_invalid_application(self, use_case, mock_message_broker):
        with pytest.raises(ValidationError):
            await use_case.execute(
                applicant_id="",
                amount=10000,
                term_months=12,
            )

        mock_message_broker.publish.assert_not_called()


class TestGetApplicationStatusUseCase:

    @pytest.fixture
    def use_case(self, mock_repository):
        return GetApplicationStatusUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_get_existing_application(self, use_case, mock_repository, sample_application):
        mock_repository.get_by_applicant_id.return_value = sample_application

        result = await use_case.execute("test_user_123")

        assert result is not None
        assert result.applicant_id == "test_user_123"

    @pytest.mark.asyncio
    async def test_get_nonexistent_application(self, use_case, mock_repository):
        mock_repository.get_by_applicant_id.return_value = None

        result = await use_case.execute("nonexistent")

        assert result is None


class TestProcessApplicationUseCase:

    @pytest.fixture
    def use_case(self, mock_repository, processor):
        return ProcessApplicationUseCase(mock_repository, processor)

    @pytest.mark.asyncio
    async def test_process_application(self, use_case, mock_repository):
        application_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "applicant_id": "user_123",
            "amount": 10000,
            "term_months": 12,
            "status": "pending",
        }

        mock_repository.save.return_value = LoanApplication(
            applicant_id="user_123",
            amount=10000,
            term_months=12,
            status=LoanApplicationStatus.APPROVED,
        )

        result = await use_case.execute(application_data)

        mock_repository.save.assert_called_once()
        assert result.status == LoanApplicationStatus.APPROVED
