from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.email_verification_code import EmailVerificationCode


class EmailVerificationCodeRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> Optional[EmailVerificationCode]:
        pass

    @abstractmethod
    async def create(self, EmailVerificationCode) -> EmailVerificationCode:
        pass

    @abstractmethod
    async def delete(self, EmailVerificationCode):
        pass
