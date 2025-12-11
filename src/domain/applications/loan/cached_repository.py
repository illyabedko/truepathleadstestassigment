from uuid import UUID

from src.domain.ports import Cache
from .entity import LoanApplication
from .ports import LoanApplicationRepository


class CachedLoanApplicationRepository(LoanApplicationRepository):

    def __init__(self, repository: LoanApplicationRepository, cache: Cache, ttl_seconds: int):
        self._repository = repository
        self._cache = cache
        self._ttl = ttl_seconds

    def _cache_key(self, applicant_id: str) -> str:
        return f"loan_application:{applicant_id}"

    async def save(self, entity: LoanApplication) -> LoanApplication:
        saved = await self._repository.save(entity)

        await self._cache.set(
            key=self._cache_key(saved.applicant_id),
            value=saved.to_dict(),
            ttl_seconds=self._ttl,
        )

        return saved

    async def get_by_id(self, entity_id: UUID) -> LoanApplication | None:
        return await self._repository.get_by_id(entity_id)

    async def get_by_applicant_id(self, applicant_id: str) -> LoanApplication | None:
        cache_key = self._cache_key(applicant_id)
        cached = await self._cache.get(cache_key)

        if cached:
            return LoanApplication.from_dict(cached)

        application = await self._repository.get_by_applicant_id(applicant_id)

        if application:
            await self._cache.set(
                key=cache_key,
                value=application.to_dict(),
                ttl_seconds=self._ttl,
            )

        return application
