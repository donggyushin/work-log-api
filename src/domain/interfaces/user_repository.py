from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User


class UserRepository(ABC):
    """User repository interface for data persistence operations"""

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass
