from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "loan-processor"
