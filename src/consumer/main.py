import asyncio
import signal
import logging

from src.domain.ports import MessageConsumer
from src.infra.db.session import async_session, init_db, close_db
from src.domain.applications.loan.use_cases import ProcessApplicationUseCase
from .dependencies import create_message_consumer, create_cache, create_repository, create_processor


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ApplicationConsumerService:

    def __init__(self, consumer: MessageConsumer):
        self._consumer = consumer
        self._processor = create_processor()
        self._cache = None

    async def start(self) -> None:
        self._cache = await create_cache()

    async def process_message(self, message: dict) -> None:
        logger.info(f"Processing application: {message.get('id')}")

        async with async_session() as session:
            repository = create_repository(session, self._cache)
            use_case = ProcessApplicationUseCase(repository, self._processor)

            try:
                application = await use_case.execute(message)
                logger.info(f"Application {application.id} processed: {application.status.value}")
            except Exception as e:
                logger.error(f"Failed to process application: {e}")

    async def run(self) -> None:
        logger.info("Starting consumer service...")

        await init_db()
        await self.start()
        await self._consumer.start()

        try:
            async for message in self._consumer.messages():
                await self.process_message(message)
        finally:
            await self._consumer.stop()
            if self._cache:
                await self._cache.disconnect()
            await close_db()
            logger.info("Consumer service stopped")

    async def stop(self) -> None:
        await self._consumer.stop()


async def main() -> None:
    consumer = create_message_consumer()
    service = ApplicationConsumerService(consumer)

    loop = asyncio.get_event_loop()

    def shutdown():
        logger.info("Shutdown signal received")
        asyncio.create_task(service.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown)

    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
