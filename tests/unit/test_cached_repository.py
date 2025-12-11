import pytest
from unittest.mock import AsyncMock

from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus
from src.domain.applications.loan.cached_repository import CachedLoanApplicationRepository


class TestCachedLoanApplicationRepository:

    @pytest.fixture
    def cached_repo(self, mock_repository, mock_cache):
        return CachedLoanApplicationRepository(
            repository=mock_repository,
            cache=mock_cache,
            ttl_seconds=3600,
        )

    @pytest.mark.asyncio
    async def test_get_from_cache(self, cached_repo, mock_repository, mock_cache):
        mock_cache.get.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "applicant_id": "user_123",
            "amount": 10000,
            "term_months": 12,
            "status": "approved",
        }

        result = await cached_repo.get_by_applicant_id("user_123")

        assert result is not None
        assert result.applicant_id == "user_123"
        mock_repository.get_by_applicant_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_from_db_on_cache_miss(self, cached_repo, mock_repository, mock_cache, sample_application):
        mock_cache.get.return_value = None
        mock_repository.get_by_applicant_id.return_value = sample_application

        result = await cached_repo.get_by_applicant_id("test_user_123")

        assert result is not None
        mock_repository.get_by_applicant_id.assert_called_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_updates_cache(self, cached_repo, mock_repository, mock_cache, sample_application):
        mock_repository.save.return_value = sample_application

        result = await cached_repo.save(sample_application)

        mock_repository.save.assert_called_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, cached_repo, mock_repository, mock_cache):
        mock_cache.get.return_value = None
        mock_repository.get_by_applicant_id.return_value = None

        result = await cached_repo.get_by_applicant_id("nonexistent")

        assert result is None
        mock_cache.set.assert_not_called()

