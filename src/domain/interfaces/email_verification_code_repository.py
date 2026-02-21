from abc import ABC, abstractmethod

from src.domain.entities.email_verification_code import EmailVerificationCode


class EmailVerificationCodeRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self) -> EmailVerificationCode:
        pass

    @abstractmethod
    async def create(self, EmailVerificationCode):
        pass

    @abstractmethod
    async def delete(self, EmailVerificationCode):
        pass
