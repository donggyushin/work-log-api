from datetime import datetime, timedelta
from src.domain.entities.email_verification_code import EmailVerificationCode
from src.domain.entities.user import User
from src.domain.interfaces.email_verification_code_repository import (
    EmailVerificationCodeRepository,
)
from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator


class ChangePasswordService:
    def __init__(
        self,
        email_verification_code_repository: EmailVerificationCodeRepository,
        verification_code_generator: VerificationCodeGenerator,
    ):
        self.email_verification_code_repository = email_verification_code_repository
        self.verification_code_generator = verification_code_generator

    async def request_verification_code(self, user: User):
        generated_code = self.verification_code_generator.generate()
        verification_code = EmailVerificationCode(
            user_id=user.id,
            email=user.email,
            code=generated_code,
            expired_at=datetime.now() + timedelta(minutes=5),
        )
        await self.email_verification_code_repository.create(verification_code)
