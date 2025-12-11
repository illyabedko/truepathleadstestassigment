import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus
from src.domain.applications.loan.ports import LoanApplicationRepository
from src.domain.applications.loan.processor import LoanApplicationProcessor, LoanProcessingRules
from src.domain.ports import Cache, MessageBroker


@pytest.fixture
def processing_rules() -> LoanProcessingRules:
    return LoanProcessingRules(
        min_amount=0,
        max_amount=1_000_000,
        min_term_months=1,
        max_term_months=60,
        approval_threshold=50_000,
    )


@pytest.fixture
def processor(processing_rules) -> LoanApplicationProcessor:
    return LoanApplicationProcessor(processing_rules)


@pytest.fixture
def sample_application() -> LoanApplication:
    return LoanApplication(
        applicant_id="test_user_123",
        amount=10000,
        term_months=12,
    )


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=LoanApplicationRepository)


@pytest.fixture
def mock_cache() -> AsyncMock:
    mock = AsyncMock(spec=Cache)
    mock.get.return_value = None
    return mock


@pytest.fixture
def mock_message_broker() -> AsyncMock:
    return AsyncMock(spec=MessageBroker)
