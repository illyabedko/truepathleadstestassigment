from pydantic_settings import SettingsConfigDict

from .app import AppSettings
from .database import DatabaseSettings
from .redis import RedisSettings
from .kafka import KafkaSettings
from .messaging import MessagingSettings
from .loan import LoanSettings


class Settings(
    AppSettings,
    DatabaseSettings,
    RedisSettings,
    KafkaSettings,
    MessagingSettings,
    LoanSettings,
):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

__all__ = ["settings"]
