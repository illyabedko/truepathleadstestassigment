from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import settings
from src.infra.db.session import get_session
from src.infra.db.loan_application.repository import PostgresLoanApplicationRepository
from src.infra.cache.redis import RedisCache
from src.infra.messaging.kafka import KafkaMessageBroker
from src.domain.ports import Cache
from src.domain.applications.loan.ports import LoanApplicationRepository
from src.domain.applications.loan.cached_repository import CachedLoanApplicationRepository
from src.domain.applications.loan.processor import LoanApplicationProcessor, LoanProcessingRules
from src.domain.applications.loan.use_cases import (
    SubmitApplicationUseCase,
    GetApplicationStatusUseCase,
)
from src.api.v1.applications import ApplicationController


# Singletons
_redis_cache: RedisCache | None = None
_kafka_broker: KafkaMessageBroker | None = None


def get_processing_rules() -> LoanProcessingRules:
    return LoanProcessingRules(
        min_amount=settings.loan_min_amount,
        max_amount=settings.loan_max_amount,
        min_term_months=settings.loan_min_term_months,
        max_term_months=settings.loan_max_term_months,
        approval_threshold=settings.loan_approval_threshold,
    )


async def get_cache() -> Cache:
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
        await _redis_cache.connect()
    return _redis_cache


async def get_kafka_broker() -> KafkaMessageBroker:
    global _kafka_broker
    if _kafka_broker is None:
        _kafka_broker = KafkaMessageBroker()
        await _kafka_broker.connect()
    return _kafka_broker


def get_processor(rules: LoanProcessingRules = Depends(get_processing_rules)) -> LoanApplicationProcessor:
    return LoanApplicationProcessor(rules)


async def get_repository(
    session: AsyncSession = Depends(get_session),
    cache: Cache = Depends(get_cache),
) -> LoanApplicationRepository:
    postgres_repo = PostgresLoanApplicationRepository(session)
    return CachedLoanApplicationRepository(
        repository=postgres_repo,
        cache=cache,
        ttl_seconds=settings.cache_ttl_seconds,
    )


async def get_submit_use_case(
    broker: KafkaMessageBroker = Depends(get_kafka_broker),
    processor: LoanApplicationProcessor = Depends(get_processor),
) -> SubmitApplicationUseCase:
    return SubmitApplicationUseCase(
        message_broker=broker,
        processor=processor,
        topic=settings.loan_application_topic,
    )


async def get_status_use_case(
    repository: LoanApplicationRepository = Depends(get_repository),
) -> GetApplicationStatusUseCase:
    return GetApplicationStatusUseCase(repository=repository)


async def get_application_controller(
    submit_use_case: SubmitApplicationUseCase = Depends(get_submit_use_case),
    get_status_use_case: GetApplicationStatusUseCase = Depends(get_status_use_case),
) -> ApplicationController:
    return ApplicationController(
        submit_use_case=submit_use_case,
        get_status_use_case=get_status_use_case,
    )


async def cleanup():
    global _redis_cache, _kafka_broker

    if _redis_cache:
        await _redis_cache.disconnect()
        _redis_cache = None

    if _kafka_broker:
        await _kafka_broker.disconnect()
        _kafka_broker = None
