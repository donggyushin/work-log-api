class DomainException(Exception):
    """Base Exception in domain layer"""


class EmailAlreadyExistsError(DomainException):
    """Raised when email already exists"""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email already exists: {email}")
