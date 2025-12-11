from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    app_name: str = "Loan Application Service"
    app_version: str = "1.0.0"
    debug: bool = False

