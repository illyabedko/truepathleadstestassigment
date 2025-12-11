from pydantic_settings import BaseSettings


class LoanSettings(BaseSettings):

    loan_min_amount: float = 0
    loan_max_amount: float = 1_000_000
    loan_min_term_months: int = 1
    loan_max_term_months: int = 60
    loan_approval_threshold: float = 50_000

