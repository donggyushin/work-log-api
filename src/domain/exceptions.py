class DomainException(Exception):
    """Base Exception in domain layer"""


class EmailAlreadyExistsError(DomainException):
    """Raised when email already exists"""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email already exists: {email}")


class PasswordLengthNotEnoughError(DomainException):
    def __init__(self, min_length: int):
        super().__init__(f"Password should be over {min_length} characters")


class UserNotFoundError(DomainException):
    def __init__(self):
        super().__init__("Can't find user")


class PasswordNotCorrectError(DomainException):
    def __init__(self):
        super().__init__("Password Not Correct")


class NotFoundError(DomainException):
    def __init__(self):
        super().__init__("Not Found Error")


class NotCorrectError(DomainException):
    def __init__(self):
        super().__init__("Not Correct Error")


class ExpiredError(DomainException):
    def __init__(self):
        super().__init__("ExpiredError")
