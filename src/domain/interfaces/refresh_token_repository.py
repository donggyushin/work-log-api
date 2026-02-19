from abc import ABC, abstractmethod


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: str):
        pass

    @abstractmethod
    async def delete(self, token: str):
        pass

    @abstractmethod
    async def exists(self, token: str) -> bool:
        pass
