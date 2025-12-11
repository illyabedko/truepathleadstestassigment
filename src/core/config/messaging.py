from pydantic_settings import BaseSettings


class MessagingSettings(BaseSettings):

    loan_application_topic: str = "loan-applications"

