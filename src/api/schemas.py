from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.applications.loan.value_objects import LoanApplicationStatus


class CreateApplicationRequest(BaseModel):
    applicant_id: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    term_months: int = Field(..., gt=0)


class ApplicationResponse(BaseModel):
    id: UUID
    applicant_id: str
    amount: float
    term_months: int
    status: LoanApplicationStatus
    rejection_reason: str | None = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    message: str
    field: str | None = None
