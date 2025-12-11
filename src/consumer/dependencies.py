from src.core import settings
from src.domain.ports import MessageConsumer, Cache
from src.domain.applications.loan.ports import LoanApplicationRepository
from src.domain.applications.loan.processor import LoanApplicationProcessor, LoanProcessingRules
from src.infra.messaging.kafka import KafkaMessageConsumer
from src.infra.cache.redis import RedisCache
from src.infra.db.loan_application.repository import PostgresLoanApplicationRepository
from src.domain.applications.loan.cached_repository import CachedLoanApplicationRepository


def create_message_consumer() -> MessageConsumer:
    return KafkaMessageConsumer()


def create_processing_rules() -> LoanProcessingRules:
    return LoanProcessingRules(
        min_amount=settings.loan_min_amount,
        max_amount=settings.loan_max_amount,
        min_term_months=settings.loan_min_term_months,
        max_term_months=settings.loan_max_term_months,
        approval_threshold=settings.loan_approval_threshold,
    )


def create_processor() -> LoanApplicationProcessor:
    rules = create_processing_rules()
    return LoanApplicationProcessor(rules)


async def create_cache() -> Cache:
    cache = RedisCache()
    await cache.connect()
    return cache


def create_repository(session, cache: Cache) -> LoanApplicationRepository:
    postgres_repo = PostgresLoanApplicationRepository(session)
    return CachedLoanApplicationRepository(
        repository=postgres_repo,
        cache=cache,
        ttl_seconds=settings.cache_ttl_seconds,
    )
