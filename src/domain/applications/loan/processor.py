from dataclasses import dataclass
from datetime import datetime

from .entity import LoanApplication
from .value_objects import LoanApplicationStatus
from src.domain.exceptions import ValidationError


@dataclass
class LoanProcessingRules:
    min_amount: float
    max_amount: float
    min_term_months: int
    max_term_months: int
    approval_threshold: float


class LoanApplicationProcessor:

    def __init__(self, rules: LoanProcessingRules):
        self._rules = rules

    def validate(self, application: LoanApplication) -> None:
        if not application.applicant_id or not application.applicant_id.strip():
            raise ValidationError("Applicant ID is required", field="applicant_id")

        if application.amount <= self._rules.min_amount:
            raise ValidationError(
                f"Amount must be greater than {self._rules.min_amount}",
                field="amount"
            )

        if application.amount > self._rules.max_amount:
            raise ValidationError(
                f"Amount must not exceed {self._rules.max_amount}",
                field="amount"
            )

        if not (self._rules.min_term_months <= application.term_months <= self._rules.max_term_months):
            raise ValidationError(
                f"Term must be between {self._rules.min_term_months} and {self._rules.max_term_months} months",
                field="term_months"
            )

    def determine_status(self, application: LoanApplication) -> LoanApplicationStatus:
        if application.amount <= self._rules.approval_threshold:
            return LoanApplicationStatus.APPROVED
        return LoanApplicationStatus.REJECTED

    def process(self, application: LoanApplication) -> LoanApplication:
        try:
            self.validate(application)
            application.status = self.determine_status(application)
            if application.status == LoanApplicationStatus.REJECTED:
                application.rejection_reason = f"Amount exceeds approval threshold of {self._rules.approval_threshold}"
        except ValidationError as e:
            application.status = LoanApplicationStatus.REJECTED
            application.rejection_reason = e.message

        application.processed_at = datetime.utcnow()
        return application
