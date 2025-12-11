class DomainError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationError(DomainError):

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)
