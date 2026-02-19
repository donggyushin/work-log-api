from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):
    """User repository interface for data persistence operations"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user in the database

        Args:
            user: User entity to create

        Returns:
            Created user with generated ID
        """
        pass
