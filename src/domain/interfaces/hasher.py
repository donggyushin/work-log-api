from abc import ABC, abstractmethod


class Hasher(ABC):
    @abstractmethod
    def hash(self, value: str) -> str:
        pass

    @abstractmethod
    def verify(self, value: str, hashed: str) -> bool:
        pass
