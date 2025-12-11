from src.domain.ports import MessageBroker
from .entity import LoanApplication
from .ports import LoanApplicationRepository
from .processor import LoanApplicationProcessor


class SubmitApplicationUseCase:

    def __init__(self, message_broker: MessageBroker, processor: LoanApplicationProcessor, topic: str):
        self._message_broker = message_broker
        self._processor = processor
        self._topic = topic

    async def execute(self, applicant_id: str, amount: float, term_months: int) -> LoanApplication:
        application = LoanApplication(
            applicant_id=applicant_id,
            amount=amount,
            term_months=term_months,
        )

        self._processor.validate(application)

        await self._message_broker.publish(
            topic=self._topic,
            message=application.to_dict(),
            key=applicant_id,
        )

        return application


class GetApplicationStatusUseCase:

    def __init__(self, repository: LoanApplicationRepository):
        self._repository = repository

    async def execute(self, applicant_id: str) -> LoanApplication | None:
        return await self._repository.get_by_applicant_id(applicant_id)


class ProcessApplicationUseCase:

    def __init__(self, repository: LoanApplicationRepository, processor: LoanApplicationProcessor):
        self._repository = repository
        self._processor = processor

    async def execute(self, application_data: dict) -> LoanApplication:
        application = LoanApplication.from_dict(application_data)

        self._processor.process(application)

        return await self._repository.save(application)
