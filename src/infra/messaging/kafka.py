import json
from typing import AsyncIterator

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from src.domain.ports import MessageBroker, MessageConsumer
from src.core import settings


class KafkaMessageBroker(MessageBroker):

    def __init__(self, bootstrap_servers: str | None = None):
        self._bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def connect(self) -> None:
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()

    async def disconnect(self) -> None:
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def publish(self, topic: str, message: dict, key: str | None = None) -> None:
        if not self._producer:
            await self.connect()

        await self._producer.send_and_wait(topic, value=message, key=key)


class KafkaMessageConsumer(MessageConsumer):

    def __init__(
        self,
        topic: str | None = None,
        bootstrap_servers: str | None = None,
        group_id: str | None = None,
    ):
        self._topic = topic or settings.loan_application_topic
        self._bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self._group_id = group_id or settings.kafka_consumer_group
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._running = True

    async def stop(self) -> None:
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None

    async def messages(self) -> AsyncIterator[dict]:
        if not self._consumer:
            raise RuntimeError("Consumer not started")

        async for message in self._consumer:
            if not self._running:
                break
            yield message.value
