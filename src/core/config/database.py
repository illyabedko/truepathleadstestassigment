from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/loan_db"
    db_pool_size: int = 5
    db_max_overflow: int = 10

