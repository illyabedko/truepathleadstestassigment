from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):

    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600

