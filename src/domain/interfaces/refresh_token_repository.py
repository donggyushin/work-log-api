from abc import ABC, abstractmethod
from typing import List


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: str, user_id: str):
        pass

    @abstractmethod
    async def delete(self, token: str):
        pass

    @abstractmethod
    async def find_tokens_by_user_id(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    async def exists(self, token: str) -> bool:
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: str):
        pass
