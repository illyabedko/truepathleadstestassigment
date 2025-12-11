import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.domain.applications.loan.entity import LoanApplication
from src.domain.applications.loan.value_objects import LoanApplicationStatus


@pytest.fixture
def mock_dependencies():
    with patch("src.api.dependencies.get_kafka_broker") as mock_broker, \
         patch("src.api.dependencies.get_cache") as mock_cache, \
         patch("src.api.dependencies.get_session"):

        mock_broker.return_value = AsyncMock()
        mock_cache.return_value = AsyncMock()
        mock_cache.return_value.get.return_value = None

        yield {
            "broker": mock_broker.return_value,
            "cache": mock_cache.return_value,
        }


@pytest.mark.asyncio
class TestApplicationAPI:

    async def test_health_check(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_create_application_success(self, mock_dependencies):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications",
                json={
                    "applicant_id": "user_123",
                    "amount": 10000,
                    "term_months": 12,
                },
            )

        assert response.status_code == 202
        data = response.json()
        assert data["applicant_id"] == "user_123"
        assert data["status"] == "pending"

    async def test_create_application_invalid(self, mock_dependencies):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications",
                json={
                    "applicant_id": "",
                    "amount": 10000,
                    "term_months": 12,
                },
            )

        assert response.status_code == 422

    async def test_get_application_not_found(self, mock_dependencies):
        with patch("src.api.dependencies.get_repository") as mock_repo:
            mock_repo.return_value = AsyncMock()
            mock_repo.return_value.get_by_applicant_id.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/applications/nonexistent")

        assert response.status_code == 404

